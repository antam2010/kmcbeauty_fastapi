#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "🚀 [STAGE] FastAPI Swarm 스택 배포 중... (docker-stack.yml)"
echo "ℹ️ docker-compose.stage.yml 제거됨 → 단일 docker-stack.yml 로 통합. 환경 구분은 .env(APP_ENV)."

# 단일 노드 로컬 Swarm 준비 (이미 활성화면 무시)
docker swarm init 2>/dev/null || true
docker network create --driver overlay --attachable shared_network_prod 2>/dev/null || true

docker build -t kmcbeauty-api:latest .
docker stack deploy -c docker-stack.yml kmcbeauty

echo "✅ 배포 완료. 호스트 포트 미공개 — 외부 NGINX가 kmcbeauty_api:3100 으로 라우팅."
