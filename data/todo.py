import os
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def get_todos_by_user(user_id: int):
    try:
        response = supabase.table("todo").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] Failed to fetch todos for user {user_id}: {e}")
        return []