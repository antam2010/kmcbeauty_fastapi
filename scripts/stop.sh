#!/bin/bash

echo "🛑 FastAPI 컨테이너 중지 중..."

# Swarm 모드인지 확인 후 제거
if docker info | grep -q "Swarm: active"; then
    docker stack rm fastapi_stack
    docker swarm leave --force
    echo "✅ Swarm 모드 종료 완료."
else
    docker-compose down
    echo "✅ 로컬 컨테이너 종료 완료."
fi
