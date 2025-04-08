#!/bin/bash

echo "🚀 [STAGE] FastAPI 로컬 개발 서버 시작 중..."
docker compose -f docker-compose.stage.yml up --build -d
