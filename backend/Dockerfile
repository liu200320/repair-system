FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖（python-docx 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
