# Smart Skill Exchange Backend Implementation

## MCP Step 1: list_tables
Attempted to use MCP table discovery first, but no MCP server/resources/templates were available in this environment.
- `list_mcp_resources` returned an empty list.
- `list_mcp_resource_templates` returned an empty list.

Because MCP database tools are unavailable here, schema delivery is provided as executable SQL in `supabase/schema.sql`.

## 1) DB Schema
Implemented in: `supabase/schema.sql`

Tables created:
- `users`
- `profiles`
- `skills`
- `skill_requests`
- `matches`
- `messages`

Highlights:
- UUID PKs
- FKs with cascade rules
- Status constraints for requests/matches
- Duplicate match prevention via unique constraint `(provider_id, skill_request_id)`
- Indexes for key access patterns
- RLS enabled with baseline policies

## 2) Backend Code (file-wise)
- App entrypoint: `app/main.py`
- Config: `app/core/config.py`
- Auth guard (bearer + Supabase session): `app/core/security.py`
- Supabase client: `app/db/supabase_client.py`
- Schemas: `app/schemas/*.py`
- Services:
  - `app/services/auth_service.py`
  - `app/services/profile_service.py`
  - `app/services/skill_service.py`
  - `app/services/request_service.py`

## 3) API Routes
Implemented endpoints:
- Auth
  - `POST /signup`
  - `POST /login`
- Profile
  - `GET /profile`
  - `POST /profile/update`
- Skills
  - `POST /skills/add`
  - `GET /skills`
- Requests and matching
  - `POST /request`
  - `GET /requests`
  - `POST /match`
  - `GET /matches`
- Messaging foundation
  - `POST /messages`

## 4) Sample Test Queries
### List users
```sql
select id, email, name, created_at from public.users order by created_at desc;
```

### Create request (SQL)
```sql
insert into public.skill_requests (requester_id, skill_name, description, status)
values ('<requester-uuid>', 'Python mentoring', 'Need help with FastAPI architecture', 'open')
returning *;
```

### Fetch matches
```sql
select * from public.matches
where requester_id = '<user-uuid>' or provider_id = '<user-uuid>'
order by created_at desc;
```

### API examples
```bash
curl -X POST http://localhost:8000/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Passw0rd!","name":"Test User"}'
```

```bash
curl -X POST http://localhost:8000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Passw0rd!"}'
```

```bash
curl -X POST http://localhost:8000/request \
  -H 'Authorization: Bearer <access-token>' \
  -H 'Content-Type: application/json' \
  -d '{"skill_name":"React","description":"Need help building dashboard"}'
```
