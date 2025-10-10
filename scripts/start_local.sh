#!/bin/bash

echo "🚀 [DEV] FastAPI 로컬 개발 서버 시작 중..."
docker compose -f docker-compose.dev.yml up --build -d
