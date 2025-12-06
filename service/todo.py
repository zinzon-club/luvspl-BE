import os
import google.generativeai as genai
import json
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def extract_json(text):
    json_match = re.search(r"\[.*\]", text, re.DOTALL)
    if not json_match:
        raise ValueError("응답에서 JSON 배열을 찾지 못했습니다.")
    return json.loads(json_match.group(0))

def generate_todo():
    prompt = """
    오늘 할 일을 6개 추천해줘.
    예시:
    [
        {"title": "운동하기", "description": "30분 운동"},
        {"title": "독서", "description": "20페이지 읽기"}
    ]
    """

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    return extract_json(raw_text)