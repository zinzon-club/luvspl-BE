import os, httpx
from data import auth as data
from utils.JWT import create_access_token

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

async def exchange_kakao_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code
    }
    if KAKAO_CLIENT_SECRET:
        data["client_secret"] = KAKAO_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        r.raise_for_status()
        return r.json()

async def fetch_kakao_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        r.raise_for_status()
        return r.json()

async def login_or_signup_kakao(code: str) -> dict:
    print("[DEBUG] login_or_signup_kakao called with code:", code)
    tokens = await exchange_kakao_token(code)
    profile = await fetch_kakao_profile(tokens["access_token"])

    kakao_id = profile["id"]
    kakao_acc = profile.get("kakao_account", {}).get("profile", {}) or profile.get("properties", {})
    nickname = kakao_acc.get("nickname")
    profile_img = kakao_acc.get("profile_image_url")

    user = data.get_user_by_kakao_id(kakao_id)
    if user is None:
        print("[DEBUG] User not found. Creating new user.")
        user = data.create_user(kakao_id, nickname, profile_img)
        print("[DEBUG] create_user returned:", user)
    else:
        print("[DEBUG] User found:", user)

    jwt_token = create_access_token({"user_id": user.get("id")})

    return {
        "access_token": jwt_token,
        "user": {
            "id": user.get("id"),
            "name": user.get("name", nickname),
            "profile": user.get("profile", profile_img)
        }
    }
