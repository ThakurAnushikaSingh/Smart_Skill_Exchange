from models.skill_model import get_all_skills, add_skill, get_user_skills


def fetch_skills():
    return get_all_skills()


def fetch_my_skills(user):
    return get_user_skills(user)


def create_skill(data):
    add_skill(data)
    return {"success": True}
