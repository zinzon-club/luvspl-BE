from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi

load_dotenv()

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os
from starlette.middleware.sessions import SessionMiddleware
from web import auth, profile, analyzer

app = FastAPI()

# 라우터 포함
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(analyzer.router)

# 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://luvspl-fe.vercel.app",
        "https://luvspl.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, session_cookie="cookie", same_site="none", https_only=True, secret_key=os.environ["SESSION_SECRET_KEY"])

# --- Swagger UI 전역 인증 설정 ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Luvspl API",
        version="1.0.0",
        description="Luvspl-BE API Documentation",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
# ---------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)