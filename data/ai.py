from fastapi import APIRouter
from dotenv import load_dotenv
from model.schemas import KakaoRequest
from service.ai import analyze_sentence

router = APIRouter()

@router.post("/bot")
async def bot(req: KakaoRequest):
    # userRequest 유효성 검사
    if not req.userRequest or not req.userRequest.get("utterance"):
        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    {"simpleText": {"text": "⚠️ 문장을 다시 입력해줘!"}}
                ]
            }
        }

    utterance = req.userRequest["utterance"]

    answer = await analyze_sentence(utterance)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": answer}}
            ]
        }
    }
