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
    # Check if any todo has been generated today
    existing_todos_count = todo_data.count_todos_today_by_user(user_id)
    print(f"DEBUG: User {user_id} has {existing_todos_count} todos generated today.")
    if existing_todos_count > 0:
        raise HTTPException(
            status_code=400,
            detail="TODO는 하루에 한 번만 생성할 수 있습니다."
        )

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
        for t in todos[:6]:
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

    if not inserted: # If no todos were inserted, it's an error
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
            "created_at": db_todo.get("created_at"),
            "user_id": db_todo.get("user_id")
        }
        formatted_todos.append(formatted_todo)
        
    return formatted_todos

def update_todo_status(todo_id: int, complete: bool | None, user_id: int):
    try:
        current_todo = todo_data.get_todo_by_id_and_user(todo_id, user_id)
        if not current_todo:
            raise HTTPException(status_code=404, detail="TODO를 찾을 수 없습니다.")

        if complete is None:
            new_complete_status = not current_todo.get("complete", False)
        else:
            new_complete_status = complete

        updated_todo = todo_data.update_todo_status(todo_id, new_complete_status, user_id)
        if updated_todo:
            formatted_todo = {
                "id": updated_todo.get("id"),
                "todos": updated_todo.get("todos"),
                "completed": updated_todo.get("complete"),
                "created_at": updated_todo.get("created_at"),
                "user_id": updated_todo.get("user_id")
            }
            return {"success": True, "todo": formatted_todo}
        else:
            raise HTTPException(status_code=404, detail="TODO를 찾을 수 없거나 업데이트할 수 없습니다.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating todo status: {e}")
        raise HTTPException(status_code=500, detail="TODO 상태 업데이트에 실패했습니다.")
