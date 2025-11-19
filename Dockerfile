FROM python:3.11-slim

# 필수 패키지 설치 (CPU + headless OpenCV용)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HuggingFace 캐싱 디렉토리 고정
ENV TRANSFORMERS_CACHE=/app/cache/huggingface

# 캐시 폴더 생성
RUN mkdir -p /app/cache/huggingface

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
