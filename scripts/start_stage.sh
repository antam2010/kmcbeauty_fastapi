#!/bin/bash
# ==============================================================================
# 단일 노드 스테이지 Swarm 배포 스크립트 (SPEC-INFRA-001)
# - 가변 `latest` 태그 미사용(REQ-INFRA-003). IMAGE_TAG 규약으로 주입한다.
# - 배포 환경 변수는 `.env.prod` 로 분리한다(REQ-INFRA-001).
# ==============================================================================
set -e
cd "$(dirname "$0")/.."

echo "🚀 [STAGE] FastAPI Swarm 스택 배포 중... (docker-stack.yml)"
echo "ℹ️ 단일 docker-stack.yml 로 통합. 배포 env 는 .env.prod(REDIS_URL=redis://redis:6379/0)."

# 로컬 단일 노드 전용 불변 태그. docker-stack.yml 의 기본값과 일치시킨다.
IMAGE_TAG="kmcbeauty-api:local"
export IMAGE_TAG

if [ ! -f .env.prod ]; then
  echo "❌ .env.prod 가 없습니다. .env.prod.example 을 복사해 값을 채우세요:"
  echo "   cp .env.prod.example .env.prod"
  exit 1
fi

# 단일 노드 로컬 Swarm 준비 (이미 활성화면 무시)
docker swarm init 2>/dev/null || true
docker network create --driver overlay --attachable shared_network_prod 2>/dev/null || true

docker build -t "$IMAGE_TAG" .
docker stack deploy -c docker-stack.yml kmcbeauty

echo "✅ 배포 완료. 호스트 포트 미공개 — 외부 NGINX가 kmcbeauty_api:3100 으로 라우팅."
