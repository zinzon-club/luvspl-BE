from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

class ProfileData:
    def update_nickname(self, user_id: int, nickname: str):
        resp = (
            supabase.table("user")
            .update({"nickname": nickname})
            .eq("id", user_id)
            .execute()
        )
        return resp.data