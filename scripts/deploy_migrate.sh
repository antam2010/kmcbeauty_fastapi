#!/bin/bash
# ==============================================================================
# 배포 전 Alembic 마이그레이션 실행 스크립트 (SPEC-INFRA-001, REQ-INFRA-005)
#
# 목적:
#   - 스택 업데이트(docker stack deploy) '이전'에 `alembic upgrade head` 를 실행한다.
#   - 마이그레이션은 하위 호환(expand/contract)을 지켜 롤링 중 구/신 레플리카가
#     동일 스키마에서 동시에 동작하도록 한다(무중단 전제). 상세 규칙은
#     docs/deployment.md 의 "마이그레이션(expand/contract)" 절 참조.
#
# 실행 방식(택1):
#   1) 매니저 노드에서 배포용 이미지로 일회성 컨테이너 실행(권장):
#        IMAGE_TAG=ghcr.io/antam2010/kmcbeauty-api:<sha> ./scripts/deploy_migrate.sh
#   2) 앱 코드가 배치된 호스트에서 직접 실행(로컬 단일 노드):
#        ./scripts/deploy_migrate.sh --local
#
# 전제:
#   - `.env.prod` 가 존재하고 DATABASE_URL 이 외부 MySQL 을 가리킨다.
#   - MySQL 은 컨테이너 외부(관리형/호스트)에 있으며 매니저 노드에서 접근 가능하다.
# ==============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env.prod ]; then
  echo "❌ .env.prod 가 없습니다. 배포 마이그레이션을 중단합니다."
  exit 1
fi

MODE="${1:-container}"

if [ "$MODE" = "--local" ]; then
  echo "🗃️  [MIGRATE] 로컬 alembic upgrade head 실행..."
  ENV=prod alembic upgrade head
else
  : "${IMAGE_TAG:?IMAGE_TAG 를 설정하세요 (예: ghcr.io/antam2010/kmcbeauty-api:<sha>)}"
  echo "🗃️  [MIGRATE] 일회성 컨테이너로 alembic upgrade head 실행... ($IMAGE_TAG)"
  # 오버레이 네트워크에 붙여 실행(외부 MySQL 접근 경로가 오버레이일 수 있음).
  docker run --rm \
    --env-file .env.prod \
    -e ENV=prod \
    --network shared_network_prod \
    "$IMAGE_TAG" \
    alembic upgrade head
fi

echo "✅ [MIGRATE] 마이그레이션 완료. 이제 스택 업데이트를 진행하세요."
