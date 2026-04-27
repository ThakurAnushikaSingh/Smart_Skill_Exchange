-- 1) Bootstrap schema
-- Paste/run full supabase/schema.sql first.

-- 2) Seed sample skills
insert into public.skills (name, description)
values
  ('Python', 'Backend and scripting'),
  ('Flask', 'Web app development'),
  ('SQL', 'Database querying')
on conflict (name) do nothing;

-- 3) Create trainer certification example (required before completion)
insert into public.certifications (user_id, skill_id, role)
values ('<trainer_uuid>', '<skill_uuid>', 'trainer')
on conflict (user_id, skill_id, role) do nothing;

-- 4) Create skill request
insert into public.skill_requests (requester_id, skill_id, status)
values ('<requester_uuid>', '<skill_uuid>', 'open')
returning *;

-- 5) Create session
insert into public.learning_sessions (trainer_id, learner_id, skill_id, scheduled_at, required_credits, meet_link, status)
values ('<trainer_uuid>', '<learner_uuid>', '<skill_uuid>', now() + interval '1 day', 3, 'https://meet.google.com/new', 'scheduled')
returning *;

-- 6) Complete session atomically
select public.complete_learning_session('<session_uuid>', '<trainer_or_learner_uuid>');

-- 7) Verify balances + transactions + certifications
select id, name, credits from public.users where id in ('<trainer_uuid>', '<learner_uuid>');
select * from public.credit_transactions order by created_at desc limit 20;
select * from public.certifications order by awarded_at desc limit 20;
