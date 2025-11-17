from fastapi import APIRouter, UploadFile, Form, Depends,Request, Security
from fastapi.security import OAuth2PasswordBearer
import pandas as pd
from transformers import pipeline
from model.sentiment_model import load_sentiment_model
from service.analysis import analyze_conversation
from data.analyze import save_analysis
from utils.security import get_current_user_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/kakao/login")
router = APIRouter()

print("Loading models...")
sentiment_model = load_sentiment_model()
classifier_model = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
print("Models loaded successfully.")

@router.post("/analyze")
async def analyze_file(request: Request, file: UploadFile, username: str = Form(...), user_id: int = Depends(get_current_user_id), token: str = Security(oauth2_scheme)):
    # 헤더 로그 출력
    print("=== REQUEST HEADERS ===")
    print(request.headers)
    print("=======================")
    df = pd.read_csv(file.file)
    result = analyze_conversation(df, username, sentiment_model, classifier_model)
    save_analysis(user_id, result)
    return result