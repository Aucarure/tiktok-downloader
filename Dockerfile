FROM python:3.11-slim

LABEL maintainer="tu-email@ejemplo.com"
LABEL description="TikTok Downloader - versión base"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]