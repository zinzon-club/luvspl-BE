import os
from supabase import create_client
from datetime import date, timedelta

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def get_todos_by_user(user_id: int):
    try:
        response = supabase.table("todo").select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(6) \
            .execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] Failed to fetch todos for user {user_id}: {e}")
        return []

def get_todo_by_id_and_user(todo_id: int, user_id: int):
    try:
        response = supabase.table("todo").select("*") \
            .eq("id", todo_id) \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"[ERROR] Failed to fetch todo {todo_id} for user {user_id}: {e}")
        return None

def count_todos_today_by_user(user_id: int):
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        print(f"DEBUG: Counting todos for user {user_id} between {today.isoformat()} and {tomorrow.isoformat()}")

        response = (
            supabase.table("todo").select("id", count='exact')
            .eq("user_id", user_id)
            .gte("created_at", today.isoformat())
            .lt("created_at", tomorrow.isoformat())
            .execute()
        )
        
        print(f"DEBUG: Supabase count response: {response.count}")
        return response.count
    except Exception as e:
        print(f"[ERROR] Failed to count todos for user {user_id}: {e}")
        return 0

def update_todo_status(todo_id: int, complete: bool, user_id: int):
    try:
        response = supabase.table("todo").update({"complete": complete}) \
            .eq("id", todo_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            print(f"[ERROR] No todo found or updated for todo_id {todo_id}, user_id {user_id}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to update todo status for todo_id {todo_id}, user_id {user_id}: {e}")
        raise e