from fastapi import APIRouter
from service.todo import generate_todo

router = APIRouter(prefix="")

@router.get("/generate")
def generate_todo_api():
    result = generate_todo()

    return {
        "success": True,
        "todos": result
    }