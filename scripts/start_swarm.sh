#!/bin/bash
set -e
cd "$(dirname "$0")/.."

APP_NAME="kmcbeauty"
IMAGE_NAME="kmcbeauty-api:latest"

echo "🚀 [PROD] FastAPI 앱 이미지 빌드 중..."
docker build -t $IMAGE_NAME .

echo "🚢 [PROD] Docker Swarm에 스택 배포 중... (docker-stack.yml)"
docker swarm init 2>/dev/null || true
docker network create --driver overlay --attachable shared_network_prod 2>/dev/null || true
docker stack deploy -c docker-stack.yml $APP_NAME

echo "✅ 배포 완료. 호스트 포트 미공개 — 외부 NGINX가 kmcbeauty_api:3100 으로 라우팅."
