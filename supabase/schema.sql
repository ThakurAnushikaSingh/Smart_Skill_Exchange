-- Smart Skill Exchange production schema
create extension if not exists "pgcrypto";

create table if not exists public.users (
  id uuid primary key,
  email text not null unique,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.profiles (
  user_id uuid primary key references public.users(id) on delete cascade,
  bio text,
  skills_offered text[] not null default '{}',
  skills_wanted text[] not null default '{}',
  updated_at timestamptz not null default now()
);

create table if not exists public.skills (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  skill_name text not null,
  description text,
  created_at timestamptz not null default now()
);

create table if not exists public.skill_requests (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid not null references public.users(id) on delete cascade,
  skill_name text not null,
  description text not null,
  status text not null default 'open' check (status in ('open', 'matched', 'completed')),
  created_at timestamptz not null default now()
);

create table if not exists public.matches (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid not null references public.users(id) on delete cascade,
  provider_id uuid not null references public.users(id) on delete cascade,
  skill_request_id uuid not null references public.skill_requests(id) on delete cascade,
  status text not null default 'pending' check (status in ('pending', 'active', 'completed', 'cancelled')),
  created_by uuid not null references public.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  constraint uniq_match unique (provider_id, skill_request_id)
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  sender_id uuid not null references public.users(id) on delete cascade,
  receiver_id uuid not null references public.users(id) on delete cascade,
  message text not null,
  timestamp timestamptz not null default now()
);

create index if not exists idx_profiles_user_id on public.profiles(user_id);
create index if not exists idx_skills_user_id on public.skills(user_id);
create index if not exists idx_skill_requests_requester_id on public.skill_requests(requester_id);
create index if not exists idx_skill_requests_status on public.skill_requests(status);
create index if not exists idx_matches_requester_id on public.matches(requester_id);
create index if not exists idx_matches_provider_id on public.matches(provider_id);
create index if not exists idx_messages_sender_receiver on public.messages(sender_id, receiver_id);

alter table public.users enable row level security;
alter table public.profiles enable row level security;
alter table public.skills enable row level security;
alter table public.skill_requests enable row level security;
alter table public.matches enable row level security;
alter table public.messages enable row level security;

-- Basic RLS policies (adjust to your trust model):
create policy if not exists "users_select_own" on public.users
for select using (auth.uid() = id);

create policy if not exists "profiles_read_all" on public.profiles
for select using (true);

create policy if not exists "profiles_write_own" on public.profiles
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy if not exists "skills_read_all" on public.skills
for select using (true);

create policy if not exists "skills_write_own" on public.skills
for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy if not exists "requests_read_all" on public.skill_requests
for select using (true);

create policy if not exists "requests_write_own" on public.skill_requests
for all using (auth.uid() = requester_id) with check (auth.uid() = requester_id);

create policy if not exists "matches_read_related" on public.matches
for select using (auth.uid() = requester_id or auth.uid() = provider_id);

create policy if not exists "matches_write_related" on public.matches
for insert with check (auth.uid() = created_by);

create policy if not exists "messages_read_related" on public.messages
for select using (auth.uid() = sender_id or auth.uid() = receiver_id);

create policy if not exists "messages_write_sender" on public.messages
for insert with check (auth.uid() = sender_id);
