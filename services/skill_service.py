from models.skill_model import get_all_skills
from models.exchange_model import get_user_skills


def fetch_skills():
    return get_all_skills()


def fetch_my_skills(user):
    user_id = user.get("id")
    if not user_id:
        return []
    return get_user_skills(user_id)
