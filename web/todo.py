from fastapi import APIRouter, Depends
from service import todo as todo_service
from utils.JWT import get_current_user

router = APIRouter()

@router.get("/generate")
def generate_todo_api(user_id: int = Depends(get_current_user)):
    saved = todo_service.generate_todo(user_id)
    return {"success": True, "todos": saved}

@router.patch("/todos/{todo_id}")
def update_todo(todo_id: int, payload: dict = {}, user_id: int = Depends(get_current_user)):
    complete = payload.get("complete")
    updated = todo_service.update_todo_status(todo_id, complete, user_id)
    return updated