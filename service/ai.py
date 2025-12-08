import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

async def analyze_sentence(text: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(text)
        return response.text
    except Exception as e:
        print("🔥 Gemini API Error:", e)
        return "⚠️ 현재 AI 서버 사용량 또는 요금 제한 때문에 응답할 수 없어요!"