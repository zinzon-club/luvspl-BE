from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os
from starlette.middleware.sessions import SessionMiddleware
from web import auth, profile
app = FastAPI()
app.include_router(auth.router)
app.include_router(profile.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, session_cookie="cookie", same_site="none", https_only=True, secret_key=os.environ["SESSION_SECRET_KEY"])

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)