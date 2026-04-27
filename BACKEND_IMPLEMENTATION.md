# Smart Skill Exchange Backend (Flask)

This project runs as a **Flask-only backend/web app**.

## Runtime
- App factory: `__init__.py` (`create_app`)
- Entrypoint: `run.py` (starts Flask development server)
- Blueprints:
  - `routes/auth_routes.py`
  - `routes/user_routes.py`
  - `routes/skill_routes.py`

## Supabase Integration
- Client config lives in `config/supabase.py`.
- Existing Flask services interact with Supabase through:
  - `services/auth_service.py`
  - `services/user_service.py`
  - `services/skill_service.py`

## Database Schema Artifact
- SQL schema remains available at: `supabase/schema.sql`.

## Notes
- Redirect guards now use `/auth` (the actual auth page route) for unauthenticated users.
- FastAPI-specific code was removed to keep the codebase Flask-only.
