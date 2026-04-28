from models.user_model import create_user, get_user_by_email, get_user_by_id_and_email
from utils.auth_utils import hash_password, verify_password





def register_user(data):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return {"error": "Name, email, and password are required"}

    if len(password) < 8:
        return {"error": "Password must be at least 8 characters"}

    if get_user_by_email(email):
        return {"error": "User already exists"}

    payload = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "dob": data.get("dob") or None,
        "gender": data.get("gender") or None,
        "bio": data.get("bio") or None,
        "credits": 21,
    }


    created = create_user(payload)
    return {"success": True, "user": created}


def login_user(email, password):
    email = (email or "").strip().lower()
    password = (password or "").strip()

    if not email or not password:
        return {"error": "Email and password are required"}

    user = get_user_by_email(email)
    if not user:
        return {"error": "Invalid credentials"}

    password_hash = user.get("password_hash")
    if not password_hash or not verify_password(password_hash, password):
        return {"error": "Invalid credentials"}

    return {"success": True, "user": user}
