import os
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def get_user_by_kakao_id(kakao_id: int):
    try:
        resp = supabase.table("user").select("*").eq("kakao_id", kakao_id).limit(1).execute()
    except Exception as e:
        print(f"[ERROR] Supabase select failed: {e}")
        return None

    data = resp.data if hasattr(resp, "data") else None
    return data[0] if data else None

def create_user(kakao_id: int, name: str, profile: str):
    try:
        resp = supabase.table("user").insert({
            "kakao_id": kakao_id,
            "name": name,
            "profile": profile,
            "nickname": ""
        }).execute()
    except Exception as e:
        print(f"[ERROR] Supabase insert failed: {e}")
        raise Exception("Failed to insert user into Supabase") from e

    data = resp.data if hasattr(resp, "data") else None
    if not data:
        raise Exception("Failed to insert user into Supabase: no data returned")

    return data[0]