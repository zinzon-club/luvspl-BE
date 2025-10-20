import os
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def get_user_by_kakao_id(kakao_id: int):
    resp = supabase.table("user").select("*").eq("kakao_id", kakao_id).limit(1).execute()
    print(resp)
    data = resp.data
    return data[0] if data else None

def create_user(kakao_id: int, name: str, profile: str):
    resp = supabase.table("user").insert({
        "kakao_id": kakao_id,
        "name": name,
        "profile": profile,
        "nickname": ""
    }).execute()

    print("[DEBUG] insert resp:", resp)
    print("[DEBUG] insert resp.data:", resp.data)

    data = resp.data
    if not data:
        raise Exception("Failed to insert user into Supabase")

    return data[0]
