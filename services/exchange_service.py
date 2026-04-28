from datetime import datetime

from models.exchange_model import (
    add_certification,
    add_user_skill,
    complete_session_atomic,
    create_session,
    create_skill_request,
    get_user_skills,
    join_session,
    list_certifications,
    list_requests_for_trainer,
    list_sessions_for_user,
    list_skill_requests,
    list_skills_catalog,
    list_transactions,
    upsert_skill,
)
from models.user_model import get_user_by_email

VALID_PROFICIENCY = {"beginner", "intermediate", "advanced", "expert"}


def request_skill_with_time(user, skill_id, suggested_time):
    user_id = user.get("id")
    if not user_id:
        return {"error": "User id missing"}
    
    if not skill_id or skill_id.strip() == "":
        return {"error": "Skill selection is required"}

    # Resolve email if needed
    if "@" in user_id:
        u = get_user_by_email(user_id)
        if u: user_id = u["id"]

    req = create_skill_request(user_id, skill_id, suggested_time)
    return {"success": True, "request": req}



def get_requests_for_user_skills(user):
    user_id = user.get("id")
    if not user_id:
        return []
    
    # Resolve email if needed
    if "@" in user_id:
        u = get_user_by_email(user_id)
        if u: user_id = u["id"]

    # 1. Get user's skills
    my_skills = get_user_skills(user_id)
    skill_ids = [s["skill_id"] for s in my_skills]
    
    # 2. Get open requests for these skills
    return list_requests_for_trainer(skill_ids)


def get_skill_requests_for_user(user):
    user_id = user.get("id")
    if not user_id:
        return []
    
    # Resolve email if needed
    if "@" in user_id:
        u = get_user_by_email(user_id)
        if u: user_id = u["id"]

    return list_skill_requests(user_id)


def add_skill_to_user(user, payload):
    user_id = user.get("id")
    if not user_id:
        return {"error": "User id missing from session"}
    
    # Resolve email to UUID if needed
    if "@" in user_id:
        u = get_user_by_email(user_id)
        if u: user_id = u["id"]

    skill_id = payload.get("skill_id")
    skill_name = (payload.get("skill_name") or payload.get("name") or "").strip()
    proficiency = (payload.get("proficiency") or "beginner").strip().lower()
    can_teach = str(payload.get("can_teach", "false")).lower() in {"true", "1", "yes", "on"}

    if not skill_id and not skill_name:
        return {"error": "Skill selection or name is required"}
    
    # If a specific skill was chosen from the list
    if skill_id and skill_id != "new":
        from config.supabase import supabase
        skill_res = supabase.table("skills").select("*").eq("id", skill_id).execute().data
        if not skill_res:
            return {"error": "Selected skill not found"}
        skill = skill_res[0]
    else:
        # Create or find by name
        if not skill_name:
            return {"error": "Skill name is required for new skills"}
        skill = upsert_skill(skill_name)

    if not skill:
        return {"error": "Failed to create/find skill"}

    add_user_skill(user_id, skill["id"], proficiency, can_teach)
    if can_teach:
        add_certification(user_id, skill["id"], "trainer")

    return {"success": True, "skill": skill}




def get_dashboard_context(user):
    user_id = user.get("id")
    if not user_id:
        return {"sessions": [], "skills_catalog": []}

    # Resolve email to UUID if session is stale
    if "@" in user_id:
        u = get_user_by_email(user_id)
        if u:
            user_id = u["id"]

    return {
        "skills_catalog": list_skills_catalog(),
        "my_skills": get_user_skills(user_id),
        "sessions": list_sessions_for_user(user_id),
    }


def create_learning_session(user, payload):
    trainer_id = user.get("id")
    request_id = payload.get("request_id")
    learner_id = (payload.get("learner_id") or "").strip() or None
    skill_id = (payload.get("skill_id") or "").strip()
    scheduled_at_raw = (payload.get("scheduled_at") or "").strip()
    required_credits = 1 # Default

    # If this is from a request, we need to get the learner_id and skill_id from it
    if request_id:
        from config.supabase import supabase
        req_data = supabase.table("skill_requests").select("*").eq("id", request_id).execute().data
        if req_data:
            req = req_data[0]
            learner_id = req["requester_id"]
            skill_id = req["skill_id"]
            # Mark request as matched
            supabase.table("skill_requests").update({"status": "matched"}).eq("id", request_id).execute()

    # Resolve emails to UUIDs for better UX
    if trainer_id and "@" in trainer_id:
        t_user = get_user_by_email(trainer_id)
        if t_user: trainer_id = t_user["id"]
    
    if learner_id and "@" in learner_id:
        l_user = get_user_by_email(learner_id)
        if l_user: learner_id = l_user["id"]
    
    if not skill_id:
        return {"error": "A skill must be selected for this session"}


    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_raw)

    except ValueError:
        return {"error": "scheduled_at must be ISO datetime"}

    created = create_session(
        trainer_id,
        learner_id,
        skill_id,
        scheduled_at,
        required_credits,
        payload.get("meet_link"),
        payload.get("trainer_notes"),
        payload.get("learner_notes"),
    )
    return {"success": True, "session": created}



def join_learning_session(user, session_id):
    learner_id = user.get("id")
    if not learner_id:
        return {"error": "User id missing from session"}
    updated = join_session(session_id, learner_id)
    if not updated:
        return {"error": "Session is not joinable"}
    return {"success": True, "session": updated[0]}


def complete_learning_session(user, session_id):
    actor_id = user.get("id")
    if not actor_id:
        return {"error": "User id missing from session"}
    result = complete_session_atomic(session_id, actor_id)
    if not result:
        return {"error": "Could not complete session"}
    return {"success": True, "result": result}


def get_transactions(user):
    user_id = user.get("id")
    if not user_id:
        return []
    return list_transactions(user_id)


def get_certifications(user):
    user_id = user.get("id")
    if not user_id:
        return []
    return list_certifications(user_id)


def request_skill(user, skill_id):
    user_id = user.get("id")
    if not user_id or not skill_id:
        return {"error": "requester_id and skill_id are required"}
    req = create_skill_request(user_id, skill_id)
    return {"success": True, "request": req}


def get_skill_requests(user):
    user_id = user.get("id")
    if not user_id:
        return []
    return list_skill_requests(user_id)
