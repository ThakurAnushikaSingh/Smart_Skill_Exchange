-- Smart Skill Exchange - one-time database setup
-- Run this file once in Supabase SQL editor.

-- 1) Ensure required columns exist
ALTER TABLE IF EXISTS sessions
    ADD COLUMN IF NOT EXISTS meeting_url text,
    ADD COLUMN IF NOT EXISTS booking_status text;

-- 2) Helpful constraints and indexes
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'bookings' AND column_name = 'status'
    ) THEN
        -- keep status controlled if table exists
        BEGIN
            ALTER TABLE bookings
            ADD CONSTRAINT bookings_status_check
            CHECK (status IN ('Pending', 'Accepted', 'Rejected', 'Completed'));
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_bookings_session_status ON bookings(session_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_teacher ON sessions(teacher_id);
CREATE INDEX IF NOT EXISTS idx_transactions_session ON transactions(session_id);

-- At most one active request (Pending/Accepted) per session
CREATE UNIQUE INDEX IF NOT EXISTS uniq_bookings_active_session
    ON bookings(session_id)
    WHERE status IN ('Pending', 'Accepted');

-- 3) Atomic booking request creator
CREATE OR REPLACE FUNCTION create_booking_request(p_session_id bigint, p_learner_id bigint)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_booking_id bigint;
    v_current_learner bigint;
BEGIN
    -- Lock session row for consistency
    SELECT learner_id
    INTO v_current_learner
    FROM sessions
    WHERE session_id = p_session_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Session not found';
    END IF;

    IF v_current_learner IS NOT NULL THEN
        RAISE EXCEPTION 'Session already assigned to a learner';
    END IF;

    IF EXISTS (
        SELECT 1 FROM bookings
        WHERE session_id = p_session_id
          AND status IN ('Pending', 'Accepted')
    ) THEN
        RAISE EXCEPTION 'Session already has an active request';
    END IF;

    INSERT INTO bookings(session_id, learner_id, status)
    VALUES (p_session_id, p_learner_id, 'Pending')
    RETURNING booking_id INTO v_booking_id;

    UPDATE sessions
    SET booking_status = 'Pending'
    WHERE session_id = p_session_id;

    RETURN v_booking_id;
END;
$$;

-- 4) Atomic accept flow (teacher provides meeting URL)
CREATE OR REPLACE FUNCTION accept_booking_request(
    p_booking_id bigint,
    p_teacher_id bigint,
    p_meeting_url text
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_session_id bigint;
    v_learner_id bigint;
    v_owner_teacher_id bigint;
BEGIN
    IF coalesce(trim(p_meeting_url), '') = '' THEN
        RAISE EXCEPTION 'Meeting URL is required';
    END IF;

    SELECT b.session_id, b.learner_id
    INTO v_session_id, v_learner_id
    FROM bookings b
    WHERE b.booking_id = p_booking_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Booking not found';
    END IF;

    SELECT teacher_id
    INTO v_owner_teacher_id
    FROM sessions
    WHERE session_id = v_session_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Session not found';
    END IF;

    IF v_owner_teacher_id <> p_teacher_id THEN
        RAISE EXCEPTION 'Not authorized to accept this booking';
    END IF;

    UPDATE bookings
    SET status = 'Accepted'
    WHERE booking_id = p_booking_id;

    UPDATE bookings
    SET status = 'Rejected'
    WHERE session_id = v_session_id
      AND booking_id <> p_booking_id
      AND status = 'Pending';

    UPDATE sessions
    SET learner_id = v_learner_id,
        meeting_url = p_meeting_url,
        booking_status = 'Accepted'
    WHERE session_id = v_session_id;

    RETURN v_session_id;
END;
$$;

-- 5) Atomic reject flow
CREATE OR REPLACE FUNCTION reject_booking_request(
    p_booking_id bigint,
    p_teacher_id bigint
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_session_id bigint;
    v_owner_teacher_id bigint;
BEGIN
    SELECT session_id
    INTO v_session_id
    FROM bookings
    WHERE booking_id = p_booking_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Booking not found';
    END IF;

    SELECT teacher_id
    INTO v_owner_teacher_id
    FROM sessions
    WHERE session_id = v_session_id
    FOR UPDATE;

    IF v_owner_teacher_id <> p_teacher_id THEN
        RAISE EXCEPTION 'Not authorized to reject this booking';
    END IF;

    UPDATE bookings
    SET status = 'Rejected'
    WHERE booking_id = p_booking_id;

    IF NOT EXISTS (
        SELECT 1 FROM bookings
        WHERE session_id = v_session_id
          AND status IN ('Pending', 'Accepted')
    ) THEN
        UPDATE sessions
        SET booking_status = NULL,
            meeting_url = NULL,
            learner_id = NULL
        WHERE session_id = v_session_id;
    END IF;

    RETURN v_session_id;
END;
$$;

-- 6) Atomic complete-session transaction
CREATE OR REPLACE FUNCTION complete_session_atomic(
    p_session_id bigint,
    p_learner_id bigint,
    p_trainer_id bigint,
    p_skill_id bigint,
    p_credits int
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_learner_credits int;
    v_trainer_credits int;
BEGIN
    IF p_credits < 0 THEN
        RAISE EXCEPTION 'Credits cannot be negative';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM certifications
        WHERE user_id = p_trainer_id
          AND skill_id = p_skill_id
          AND role = 'TRAINER'
    ) THEN
        RAISE EXCEPTION 'Trainer is not certified';
    END IF;

    UPDATE bookings
    SET status = 'Completed'
    WHERE session_id = p_session_id
      AND status = 'Accepted';

    INSERT INTO transactions(session_id, learner_id, trainer_id, credits_transferred)
    VALUES (p_session_id, p_learner_id, p_trainer_id, p_credits);

    SELECT credits INTO v_learner_credits
    FROM users
    WHERE user_id = p_learner_id
    FOR UPDATE;

    SELECT credits INTO v_trainer_credits
    FROM users
    WHERE user_id = p_trainer_id
    FOR UPDATE;

    IF v_learner_credits IS NULL OR v_trainer_credits IS NULL THEN
        RAISE EXCEPTION 'Learner or trainer not found';
    END IF;

    IF v_learner_credits < p_credits THEN
        RAISE EXCEPTION 'Insufficient learner credits';
    END IF;

    UPDATE users
    SET credits = v_learner_credits - p_credits
    WHERE user_id = p_learner_id;

    UPDATE users
    SET credits = v_trainer_credits + p_credits
    WHERE user_id = p_trainer_id;

    INSERT INTO certifications(user_id, skill_id, role)
    SELECT p_learner_id, p_skill_id, 'LEARNER'
    WHERE NOT EXISTS (
        SELECT 1 FROM certifications
        WHERE user_id = p_learner_id
          AND skill_id = p_skill_id
    );
END;
$$;
