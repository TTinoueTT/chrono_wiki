FROM python:3.13.5-slim-bullseye

WORKDIR /app

# ビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 環境変数に基づいて適切なrequirementsファイルを選択
ARG ENVIRONMENT=production
COPY requirements-base.txt .
COPY requirements-${ENVIRONMENT}.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# デフォルトのコマンドを設定
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]