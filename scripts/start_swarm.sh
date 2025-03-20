#!/bin/bash

APP_NAME="myapp"
IMAGE_NAME="fastapi-app:latest"

echo "🚀 [PROD] FastAPI 앱 이미지 빌드 중..."
docker build -t $IMAGE_NAME .

echo "🚢 [PROD] Docker Swarm에 스택 배포 중..."
docker stack deploy -c docker-compose.prod.yml $APP_NAME
