from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

def load_sentiment_model(model_name="jaehyeong/koelectra-base-v3-generalized-sentiment-analysis"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    return analyzer
