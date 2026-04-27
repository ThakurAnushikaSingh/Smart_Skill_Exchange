from models.skill_model import get_all_skills, add_skill

def fetch_skills():
    return get_all_skills()

def create_skill(data):
    add_skill(data)
    return {"success": True}