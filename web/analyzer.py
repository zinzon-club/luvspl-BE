from fastapi import APIRouter, UploadFile, Form, Depends
import pandas as pd
from transformers import pipeline
from model.sentiment_model import load_sentiment_model
from service.analysis import analyze_conversation
from data.analyze import save_analysis
from utils.security import get_current_user_id

router = APIRouter()

print("Loading models...")
sentiment_model = load_sentiment_model()
classifier_model = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
print("Models loaded successfully.")

@router.post("/analyze")
async def analyze_file(file: UploadFile, username: str = Form(...), user_id: int = Depends(get_current_user_id)):
    df = pd.read_csv(file.file)
    result = analyze_conversation(df, username, sentiment_model, classifier_model)
    save_analysis(user_id, result)
    return result