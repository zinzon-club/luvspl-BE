from fastapi import APIRouter, UploadFile, Form
import pandas as pd
from transformers import pipeline
from model.sentiment_model import load_sentiment_model
from service.analysis import analyze_conversation

router = APIRouter()

print("Loading models...")
sentiment_model = load_sentiment_model()
classifier_model = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
print("Models loaded successfully.")

@router.post("/analyze")
async def analyze_file(file: UploadFile, username: str = Form(...)):
    df = pd.read_csv(file.file)
    result = analyze_conversation(df, username, sentiment_model, classifier_model)
    return result