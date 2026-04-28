from config.supabase import supabase


def create_user(data):
    res = supabase.table("users").insert(data).execute()
    return res.data[0] if res.data else None


def get_user_by_email(email):
    res = supabase.table("users").select("*").eq("email", email).limit(1).execute()
    return res.data[0] if res.data else None


def get_user_by_id(user_id):
    res = supabase.table("users").select("*").eq("id", user_id).limit(1).execute()
    return res.data[0] if res.data else None


def get_user_by_id_and_email(user_id, email):
    res = (
        supabase.table("users")
        .select("*")
        .eq("id", user_id)
        .eq("email", email)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None
