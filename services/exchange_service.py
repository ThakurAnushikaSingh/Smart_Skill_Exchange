from datetime import datetime

from models.exchange_model import (
    add_user_skill,
    complete_session_atomic,
    create_session,
    get_user_skills,
    join_session,
    list_certifications,
    list_sessions_for_user,
    list_skills_catalog,
    list_transactions,
    upsert_skill,
    create_skill_request,
    list_skill_requests,
)

VALID_PROFICIENCY = {"beginner", "intermediate", "advanced", "expert"}


def add_skill_to_user(user, payload):
    user_id = user.get("id")
    if not user_id:
        return {"error": "User id missing from session"}

    skill_name = (payload.get("skill_name") or payload.get("name") or "").strip()
    proficiency = (payload.get("proficiency") or "beginner").strip().lower()
    can_teach = str(payload.get("can_teach", "false")).lower() in {"true", "1", "yes", "on"}

    if not skill_name:
        return {"error": "Skill name is required"}
    if proficiency not in VALID_PROFICIENCY:
        return {"error": "Invalid proficiency level"}

    skill = upsert_skill(skill_name)
    if not skill:
        return {"error": "Failed to create/find skill"}

    add_user_skill(user_id, skill["id"], proficiency, can_teach)
    return {"success": True, "skill": skill}


def get_dashboard_context(user):
    user_id = user.get("id")
    if not user_id:
        return {"skills_catalog": [], "my_skills": [], "sessions": []}
    return {
        "skills_catalog": list_skills_catalog(),
        "my_skills": get_user_skills(user_id),
        "sessions": list_sessions_for_user(user_id),
    }


def create_learning_session(user, payload):
    trainer_id = user.get("id")
    learner_id = (payload.get("learner_id") or "").strip() or None
    skill_id = (payload.get("skill_id") or "").strip()
    scheduled_at_raw = (payload.get("scheduled_at") or "").strip()

    try:
        required_credits = int(payload.get("required_credits", 1))
    except (TypeError, ValueError):
        return {"error": "required_credits must be a number"}

    if not trainer_id or not skill_id or not scheduled_at_raw:
        return {"error": "trainer, skill and scheduled time are required"}
    if required_credits <= 0:
        return {"error": "required_credits must be greater than 0"}

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
