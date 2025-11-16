from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

class TodoData:
    def create_todo(self, text: str, completed: bool = False):
        resp = (
            supabase.table("todo")
            .insert({
                "todo": text,
                "completed": completed
            })
            .execute()
        )
        return resp.data

    def get_todos(self):
        resp = (
            supabase.table("todo")
            .select("*")
            .execute()
        )
        return resp.data