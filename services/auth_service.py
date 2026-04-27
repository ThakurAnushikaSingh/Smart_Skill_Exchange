from models.user_model import create_user, get_user_by_email, get_user_by_id_and_email


def register_user(data):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    if not name or not email:
        return {"error": "Name and email are required"}

    if get_user_by_email(email):
        return {"error": "User already exists"}

    created = create_user({"name": name, "email": email})
    return {"success": True, "user": created}


def login_user(user_id, email):
    user_id = (user_id or "").strip()
    email = (email or "").strip().lower()
    if not user_id or not email:
        return {"error": "user_id and email are required"}

    user = get_user_by_id_and_email(user_id, email)
    if not user:
        return {"error": "Invalid user_id or email"}

    return {"success": True, "user": user}
