#!/bin/bash

echo "🛑 FastAPI 중지 중..."

# Swarm 스택 배포(start_swarm.sh) 사용 시 제거. docker-compose 구성은 제거됨.
if docker info 2>/dev/null | grep -q "Swarm: active"; then
    docker stack rm kmcbeauty
    echo "✅ Swarm 스택(kmcbeauty) 제거 완료."
else
    echo "ℹ️ Swarm 비활성 — 제거할 스택 없음. 로컬 개발 서버(uvicorn)는 Ctrl+C 로 종료."
fi
