from fastapi import APIRouter, Depends
from service import todo as todo_service
from utils.JWT import get_current_user

router = APIRouter()

@router.get("/generate")
def generate_todo_api(user_id: int = Depends(get_current_user)):
    saved = todo_service.generate_todo(user_id)
    return {"success": True, "todos": saved}

@router.get("/todos")
def get_todos_api(user_id: int = Depends(get_current_user)):
    todos = todo_service.get_user_todos(user_id)
    return {"success": True, "todos": todos}