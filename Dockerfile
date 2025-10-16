# -------------------------------
# ✅ OCR Evaluation Platform Dockerfile
# -------------------------------
FROM python:3.12

# 設定工作目錄
WORKDIR /app

# 複製 requirements 並安裝相依套件
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 複製應用程式碼
COPY app/ ./app/

# 創建資料目錄（用於掛載 volume）
RUN mkdir -p data/uploads

# 暴露服務埠
EXPOSE 8080

# 啟動伺服器
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
