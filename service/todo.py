import os
import google.generativeai as genai
import json
import re
from supabase import create_client
from fastapi import HTTPException
from data import todo as todo_data

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print("="*50)
print(f"DEBUG: Loaded SUPABASE_URL: '{SUPABASE_URL}'")
print(f"DEBUG: Loaded SUPABASE_SERVICE_KEY: '{SUPABASE_SERVICE_KEY}'")
print("="*50)

if not SUPABASE_SERVICE_KEY or not SUPABASE_URL:
    raise RuntimeError(
        "FATAL: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in your environment."
    )
if "anon" in SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "FATAL: SUPABASE_SERVICE_KEY is set to the public 'anon' key. "
        "You must use the secret 'service_role' key to bypass RLS."
    )
if SUPABASE_SERVICE_KEY.count('.') != 2:
     raise RuntimeError(
        "FATAL: SUPABASE_SERVICE_KEY does not look like a valid JWT. "
        "Please get the secret 'service_role' key from your Supabase project's API settings."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def extract_json(text):
    match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if not match:
        print(f"Failed to find JSON array in response: {text}")
        raise ValueError("응답에서 JSON 배열을 찾지 못했습니다.")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(f"Malformed JSON string: {match.group(0)}")
        raise ValueError("응답의 JSON 형식이 올바르지 않습니다.")

def generate_todo(user_id: int):
    prompt = """
    오늘 할 일을 6개 추천해줘. 그런데 추천 항목은 모두 언어습관에 관련된 할 일이면 좋겠어.
    출력은 JSON 배열만:
    [
        {"title": "...", "description": "..."},
        ...
    ]
    """

    try:
        response = model.generate_content(prompt)
        response_text = ''.join(part.text for part in response.parts) if response.parts else response.text
        todos = extract_json(response_text.strip())
    except Exception as e:
        print(f"Error during Gemini API call or JSON extraction: {e}")
        raise HTTPException(status_code=500, detail="TODO 목록 생성에 실패했습니다. (Gemini API)")

    inserted = []
    try:
        for t in todos:
            response = supabase.table("todo").insert({
                "todos": t["title"],
                "user_id": user_id,
                "complete": False
            }).execute()

            if response.data and len(response.data) > 0:
                inserted.append(response.data[0])
            else:
                print(f"Supabase insert for todo '{t['title']}' returned no data.")

    except Exception as e:
        print(f"Error during Supabase insert: {e}")
        raise HTTPException(status_code=500, detail="TODO 목록 저장에 실패했습니다. (Database)")

    if not inserted:
        raise HTTPException(status_code=500, detail="생성된 TODO를 데이터베이스에 저장하지 못했습니다.")

    return inserted

def get_user_todos(user_id: int):
    db_todos = todo_data.get_todos_by_user(user_id)
    
    formatted_todos = []
    for db_todo in db_todos:
        formatted_todo = {
            "id": db_todo.get("id"),
            "todos": db_todo.get("todos"),
            "completed": db_todo.get("complete"),
            "created_at": db_todo.get("create_at"),
            "user_id": db_todo.get("user_id")
        }
        formatted_todos.append(formatted_todo)
        
    return formatted_todos