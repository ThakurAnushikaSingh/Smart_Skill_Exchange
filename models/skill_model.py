from config.supabase import supabase


def get_all_skills():
    res = supabase.table("skills").select("*").order("name").execute()
    return res.data


def add_skill(data):
    return supabase.table("skills").insert(data).execute()
