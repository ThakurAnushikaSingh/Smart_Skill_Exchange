from config.supabase import supabase


def get_all_skills():
    res = supabase.table("skills").select("*").execute()
    return res.data


def add_skill(data):
    return supabase.table("skills").insert(data).execute()


def get_user_skills(user):
    """Best-effort ownership filtering without hard-coding a strict schema."""
    skills = get_all_skills() or []
    user_id = user.get("id")
    user_email = user.get("email")

    my_skills = []
    for skill in skills:
        owners = [
            skill.get("user_id"),
            skill.get("owner_id"),
            skill.get("created_by"),
            skill.get("email"),
            skill.get("owner_email"),
            skill.get("user_email"),
        ]

        if (user_id and user_id in owners) or (user_email and user_email in owners):
            my_skills.append(skill)

    return my_skills
