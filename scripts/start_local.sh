#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "🚀 [DEV] FastAPI 로컬 개발 서버 시작 중... (uvicorn :3200)"
echo "ℹ️ docker-compose 구성은 제거됨 — 컨테이너 배포는 docker-stack.yml(Swarm) 사용."
echo "ℹ️ REDIS_URL 미설정 시 기본값 redis://redis:6379/0 — 로컬 redis 필요."

uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-3200}" --reload
