#!/bin/bash

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. 환경 변수를 설정하세요."
    exit 1
fi

# FastAPI 이미지 빌드
echo "🚀 FastAPI Docker 이미지 빌드 중..."
docker build -t fastapi-app .

# 기본적으로 로컬에서 실행
echo "🛠️  Docker Compose로 로컬 컨테이너 실행 중..."
docker-compose up -d
echo "✅ FastAPI 컨테이너가 로컬에서 실행되었습니다."
echo "📡 http://localhost:8000/docs 에서 API 확인 가능"

# Swarm 모드 실행 옵션 추가
if [[ "$1" == "swarm" ]]; then
    echo "🛠️  Docker Swarm 모드 확인 중..."
    docker swarm init 2>/dev/null || echo "✅ Swarm 모드가 이미 활성화되어 있습니다."

    # 네트워크 생성 (이미 존재하면 무시)
    docker network create --driver overlay fastapi_network 2>/dev/null || echo "✅ 네트워크가 이미 존재합니다."

    # Swarm 모드에서 서비스 배포
    echo "🚀 Swarm 모드에서 FastAPI 서비스 배포 중..."
    docker stack deploy -c docker-compose.yml fastapi_stack

    echo "✅ FastAPI 서비스가 Docker Swarm에서 실행되었습니다."
    echo "📡 http://localhost:8000/docs 에서 API 확인 가능"
fi
