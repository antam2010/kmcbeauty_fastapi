#!/bin/bash

echo "🛠️ Swarm 모드 초기화 중..."
docker swarm init 2>/dev/null || echo "✅ Swarm 모드가 이미 활성화되어 있습니다."

echo "🛠️ Swarm 네트워크 확인 중..."
docker network create --driver overlay --attachable fastapi_network 2>/dev/null || echo "✅ 네트워크가 이미 존재합니다."

echo "🚀 FastAPI Docker 이미지 빌드 중..."
docker build -t fastapi-app .

echo "🚀 Swarm 모드에서 FastAPI 서비스 배포 중..."
docker stack deploy -c docker-compose.yml fastapi_stack

echo "✅ Swarm 모드에서 FastAPI 서비스가 실행되었습니다."
echo "📡 http://localhost:8000/docs 에서 API 확인 가능"
