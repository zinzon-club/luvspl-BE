from fastapi import APIRouter
from data.todo import TodoData
from data.analysis import AnalysisData
from google import genai
import os

router = APIRouter(prefix="/todo")

@router.post("/generate")
def generate_todo(req: dict):

    # DB에서 분석 데이터 가져오기
    analysis_data = AnalysisData()
    analysis = analysis_data.get_analysis(1)  # 예시: ID 1 고정

    # Gemini로 TODO 생성
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    아래 분석 데이터를 바탕으로 사용자의 대화 개선을 위한 TODO 제목만 5개 만들어줘.
    형식: ["todo1", "todo2", "todo3", ...]

    분석 데이터:
    {analysis}
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    todos = eval(response.text)

    # 저장
    todo_data = TodoData()
    saved = []

    for title in todos:
        result = todo_data.create_todo(
            text=title,
            completed=False
        )
        saved.append(result)

    return {
        "success": True,
        "count": len(saved),
        "data": saved
    }