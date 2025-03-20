#!/bin/bash

echo "🚀 로컬 개발 환경 실행 중..."
docker-compose up -d

if [[ "$(docker images -q fastapi-app 2> /dev/null)" == "" ]]; then
    echo "🔄 FastAPI Docker 이미지가 없어서 빌드 중..."
    docker build -t fastapi-app .
fi

echo "✅ FastAPI가 로컬에서 실행되었습니다."
echo "📡 http://localhost:8000/docs 에서 API 확인 가능"
