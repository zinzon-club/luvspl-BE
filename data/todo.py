from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

class TodoData:
    def create_todo(self, text: str, completed: bool = False, created_at: str = None):
        if created_at is None:
            created_at = datetime.now().strftime("%Y-%m-%d")

        resp = (
            self.supabase.table("todo")
            .upsert({
                "id": id,
                "todos": text,
                "completed": completed,
                "created_at": created_at,
                "user_id": user_id
            })
            .execute()
        )
        return resp.data

    def get_todos(self):
        resp = (
            self.supabase.table("todo")
            .select("*")
            .execute()
        )
        return resp.data