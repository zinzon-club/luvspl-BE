from fastapi import APIRouter
from pydantic import BaseModel
from data.todo import TodoData

router = APIRouter()

@router.post("/todo")
def create_todo(req: Todo):
    todo_data = TodoData()
    data = todo_data.create_todo(req.text, req.completed)
    return {"success": True, "data": data}

@router.get("/todo")
def get_todos():
    todo_data = TodoData()
    data = todo_data.get_todos()
    return {"success": True, "data": data}