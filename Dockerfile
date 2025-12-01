FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN python - <<EOF
from transformers import AutoTokenizer, AutoModel
AutoTokenizer.from_pretrained("beomi/KcELECTRA-base-v2022")
AutoModel.from_pretrained("beomi/KcELECTRA-base-v2022")
print("Model download complete.")
EOF

COPY . .

# HuggingFace 재다운로드 방지
ENV HF_HUB_OFFLINE=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
