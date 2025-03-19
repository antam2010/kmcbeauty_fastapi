#!/bin/bash

echo "🔄 서버 배포 시작..."

# 1. 최신 코드 가져오기
echo "🚀 최신 코드 Pull 중..."
git pull origin main || { echo "❌ Git Pull 실패"; exit 1; }

# 2. 컨테이너 재시작 (필요한 경우)
echo "🛠️ Docker 컨테이너 재시작 중..."
docker compose down || { echo "❌ 컨테이너 중지 실패"; exit 1; }
docker compose up --build -d || { echo "❌ 컨테이너 시작 실패"; exit 1; }

# 3. Alembic 마이그레이션 적용
echo "📦 Alembic 마이그레이션 실행 중..."
docker compose exec api alembic upgrade head || { echo "❌ Alembic 마이그레이션 실패"; exit 1; }

echo "✅ 서버 배포 완료!"
