# Python 3.11 이미지 사용
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정 (UTF-8 및 PYTHONUNBUFFERED)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 시스템 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# FastAPI 애플리케이션 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 코드 볼륨 마운트
VOLUME ["/app"]
VOLUME ["/scripts"]
VOLUME ["/logs"]

# 컨테이너가 실행될 때 FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
