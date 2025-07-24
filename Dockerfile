FROM python:3.13.5-slim-bullseye

# タイムゾーンをJSTに設定
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# ビルドに必要なツールをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    vim \
    gnupg2 \
    socat \
    readline-common \
    libreadline-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# GPGの設定
RUN mkdir -p /root/.gnupg && \
    chmod 700 /root/.gnupg && \
    echo 'pinentry-program /usr/bin/pinentry-curses' > /root/.gnupg/gpg-agent.conf

# 環境変数に基づいて適切なrequirementsファイルを選択
ARG ENVIRONMENT=production
COPY requirements-base.txt .
COPY requirements-${ENVIRONMENT}.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# デフォルトのコマンドを設定
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]