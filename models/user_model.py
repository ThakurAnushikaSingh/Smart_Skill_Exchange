from config.supabase import supabase

def create_user(data):
    return supabase.table("users").insert(data).execute()

def get_user_by_email(email):
    res = supabase.table("users").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None