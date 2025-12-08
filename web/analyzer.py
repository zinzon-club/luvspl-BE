from fastapi import APIRouter, UploadFile, Form, HTTPException, Query
import pandas as pd
from transformers import pipeline
from model.sentiment_model import load_sentiment_model
from service.analysis import analyze_conversation
from data.analyze import save_analysis, get_analyses_by_user

router = APIRouter()

print("Loading models...")
sentiment_model = load_sentiment_model()
classifier_model = pipeline(
    "zero-shot-classification", model="joeddav/xlm-roberta-large-xnli"
)
print("Models loaded successfully.")


@router.post("/analyze")
async def analyze_file(
    file: UploadFile,
    username: str = Form(...),
    user_id: int = Query(...)
):

    df = pd.read_csv(file.file)
    result = analyze_conversation(df, username, sentiment_model, classifier_model)
    save_analysis(user_id, result)
    return result


@router.get("/analyze/history")
async def get_analysis_history(user_id: int):
    try:
        analyses = get_analyses_by_user(user_id)
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch analysis history: {e}")
    return {"user_id": user_id, "analyses": analyses}