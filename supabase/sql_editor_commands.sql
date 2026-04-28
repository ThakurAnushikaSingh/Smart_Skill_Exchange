-- Smart Skill Exchange: DB migration + verification commands for Supabase SQL Editor
-- Run this file top-to-bottom.

create extension if not exists "pgcrypto";

-- === Users ===
alter table if exists public.users add column if not exists password_hash text;
alter table if exists public.users add column if not exists bio text;
alter table if exists public.users add column if not exists dob date;
alter table if exists public.users add column if not exists gender text;
alter table if exists public.users add column if not exists credits integer not null default 25;

-- === Skills + User Skills ===
create table if not exists public.skills (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  description text,
  created_at timestamptz not null default now()
);

create table if not exists public.user_skills (
  user_id uuid not null references public.users(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  proficiency text not null check (proficiency in ('beginner','intermediate','advanced','expert')),
  can_teach boolean not null default false,
  created_at timestamptz not null default now(),
  primary key (user_id, skill_id)
);

-- === Skill Requests ===
create table if not exists public.skill_requests (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid not null references public.users(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  status text not null default 'open' check (status in ('open','matched','cancelled')),
  created_at timestamptz not null default now()
);

-- === Sessions ===
create table if not exists public.learning_sessions (
  id uuid primary key default gen_random_uuid(),
  trainer_id uuid not null references public.users(id) on delete cascade,
  learner_id uuid references public.users(id) on delete set null,
  skill_id uuid not null references public.skills(id) on delete restrict,
  scheduled_at timestamptz not null,
  required_credits integer not null check (required_credits > 0),
  meet_link text,
  trainer_notes text,
  learner_notes text,
  status text not null default 'scheduled' check (status in ('scheduled','in_progress','completed','cancelled')),
  completed_at timestamptz,
  created_at timestamptz not null default now()
);

-- === Certifications ===
create table if not exists public.certifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  skill_id uuid not null references public.skills(id) on delete cascade,
  role text not null check (role in ('trainer','learner')),
  source_session_id uuid references public.learning_sessions(id) on delete set null,
  awarded_at timestamptz not null default now(),
  unique (user_id, skill_id, role)
);

-- === Credit Transactions ===
create table if not exists public.credit_transactions (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.learning_sessions(id) on delete cascade,
  from_user_id uuid not null references public.users(id) on delete cascade,
  to_user_id uuid not null references public.users(id) on delete cascade,
  amount integer not null check (amount > 0),
  reason text not null default 'session_completion',
  created_at timestamptz not null default now(),
  unique (session_id)
);

-- Indexes
create index if not exists idx_user_skills_skill on public.user_skills(skill_id);
create index if not exists idx_sessions_trainer on public.learning_sessions(trainer_id);
create index if not exists idx_skill_requests_requester on public.skill_requests(requester_id);
create index if not exists idx_sessions_learner on public.learning_sessions(learner_id);
create index if not exists idx_sessions_status on public.learning_sessions(status);
create index if not exists idx_transactions_from on public.credit_transactions(from_user_id);
create index if not exists idx_transactions_to on public.credit_transactions(to_user_id);
create index if not exists idx_certifications_user on public.certifications(user_id);

-- Atomic completion function
create or replace function public.complete_learning_session(p_session_id uuid, p_actor_id uuid)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_session public.learning_sessions%rowtype;
  v_learner_credits integer;
begin
  select * into v_session
  from public.learning_sessions
  where id = p_session_id
  for update;

  if not found then
    raise exception 'session_not_found';
  end if;

  if v_session.status <> 'scheduled' then
    raise exception 'session_not_completable';
  end if;

  if v_session.learner_id is null then
    raise exception 'session_has_no_learner';
  end if;

  if p_actor_id <> v_session.trainer_id and p_actor_id <> v_session.learner_id then
    raise exception 'actor_not_authorized';
  end if;

  if not exists (
    select 1 from public.certifications
    where user_id = v_session.trainer_id and skill_id = v_session.skill_id and role = 'trainer'
  ) then
    raise exception 'trainer_not_certified';
  end if;

  select credits into v_learner_credits from public.users where id = v_session.learner_id for update;
  if v_learner_credits < v_session.required_credits then
    raise exception 'insufficient_credits';
  end if;

  update public.users set credits = credits - v_session.required_credits where id = v_session.learner_id;
  update public.users set credits = credits + v_session.required_credits where id = v_session.trainer_id;

  update public.learning_sessions
  set status = 'completed', completed_at = now()
  where id = v_session.id;

  insert into public.credit_transactions(session_id, from_user_id, to_user_id, amount)
  values (v_session.id, v_session.learner_id, v_session.trainer_id, v_session.required_credits)
  on conflict (session_id) do nothing;

  insert into public.certifications(user_id, skill_id, role, source_session_id)
  values (v_session.learner_id, v_session.skill_id, 'learner', v_session.id)
  on conflict (user_id, skill_id, role) do nothing;

  return jsonb_build_object(
    'session_id', v_session.id,
    'status', 'completed',
    'credits_moved', v_session.required_credits
  );
end;
$$;

-- verification
select table_name from information_schema.tables where table_schema='public' and table_name in
('users','skills','user_skills','skill_requests','learning_sessions','certifications','credit_transactions')
order by table_name;
