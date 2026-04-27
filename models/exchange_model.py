from datetime import datetime
from config.supabase import supabase


SKILLS_TABLE = "skills"
USER_SKILLS_TABLE = "user_skills"
SESSIONS_TABLE = "learning_sessions"
TRANSACTIONS_TABLE = "credit_transactions"
CERTIFICATIONS_TABLE = "certifications"
SKILL_REQUESTS_TABLE = "skill_requests"


def list_skills_catalog():
    return supabase.table(SKILLS_TABLE).select("*").order("name").execute().data


def upsert_skill(name):
    name = (name or "").strip()
    if not name:
        return None
    existing = supabase.table(SKILLS_TABLE).select("*").ilike("name", name).limit(1).execute().data
    if existing:
        return existing[0]
    payload = {"name": name}
    return supabase.table(SKILLS_TABLE).insert(payload).execute().data[0]


def add_user_skill(user_id, skill_id, proficiency, can_teach):
    payload = {
        "user_id": user_id,
        "skill_id": skill_id,
        "proficiency": proficiency,
        "can_teach": can_teach,
    }
    return supabase.table(USER_SKILLS_TABLE).upsert(payload, on_conflict="user_id,skill_id").execute().data


def get_user_skills(user_id):
    return (
        supabase.table(USER_SKILLS_TABLE)
        .select("*, skill:skills(id,name)")
        .eq("user_id", user_id)
        .execute()
        .data
    )


def create_session(trainer_id, learner_id, skill_id, scheduled_at, required_credits):
    payload = {
        "trainer_id": trainer_id,
        "learner_id": learner_id,
        "skill_id": skill_id,
        "scheduled_at": scheduled_at.isoformat() if isinstance(scheduled_at, datetime) else scheduled_at,
        "required_credits": required_credits,
        "status": "scheduled",
    }
    return supabase.table(SESSIONS_TABLE).insert(payload).execute().data[0]


def list_sessions_for_user(user_id):
    return (
        supabase.table(SESSIONS_TABLE)
        .select("*, skill:skills(id,name)")
        .or_(f"trainer_id.eq.{user_id},learner_id.eq.{user_id}")
        .order("scheduled_at", desc=False)
        .execute()
        .data
    )


def join_session(session_id, learner_id):
    return (
        supabase.table(SESSIONS_TABLE)
        .update({"learner_id": learner_id, "status": "scheduled"})
        .eq("id", session_id)
        .is_("learner_id", "null")
        .execute()
        .data
    )


def complete_session_atomic(session_id, actor_id):
    payload = {"p_session_id": session_id, "p_actor_id": actor_id}
    return supabase.rpc("complete_learning_session", payload).execute().data


def list_transactions(user_id):
    return (
        supabase.table(TRANSACTIONS_TABLE)
        .select("*")
        .or_(f"from_user_id.eq.{user_id},to_user_id.eq.{user_id}")
        .order("created_at", desc=True)
        .execute()
        .data
    )


def list_certifications(user_id):
    return (
        supabase.table(CERTIFICATIONS_TABLE)
        .select("*, skill:skills(id,name)")
        .eq("user_id", user_id)
        .order("awarded_at", desc=True)
        .execute()
        .data
    )


def create_skill_request(requester_id, skill_id):
    payload = {"requester_id": requester_id, "skill_id": skill_id, "status": "open"}
    return supabase.table(SKILL_REQUESTS_TABLE).insert(payload).execute().data[0]


def list_skill_requests(user_id):
    return (
        supabase.table(SKILL_REQUESTS_TABLE)
        .select("*, skill:skills(id,name)")
        .eq("requester_id", user_id)
        .order("created_at", desc=True)
        .execute()
        .data
    )
