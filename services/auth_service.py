from models.user_model import create_user, get_user_by_email
from utils.auth_utils import hash_password, verify_password

def register_user(data):
    if get_user_by_email(data["email"]):
        return {"error": "User already exists"}

    data["password_hash"] = hash_password(data["password"])
    del data["password"]

    create_user(data)
    return {"success": True}

def login_user(email, password):
    user = get_user_by_email(email)

    if not user:
        return {"error": "User not found"}

    if not verify_password(user["password_hash"], password):
        return {"error": "Invalid credentials"}

    return {"success": True, "user": user}