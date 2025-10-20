import os, jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(payload: dict, expires_delta: timedelta = timedelta(minutes=60)):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode.update({"iat": now, "exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
