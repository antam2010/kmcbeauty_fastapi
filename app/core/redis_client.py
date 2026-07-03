import os

import redis

# Redis 접속 URL은 환경변수로 주입한다.
# - Swarm 에서는 항상 서비스 이름(redis)으로 접근하므로 기본값을 서비스 이름으로 둔다.
# - 로컬 개발 등에서는 REDIS_URL 환경변수로 오버라이드할 수 있다.
#   (예: redis://localhost:6379/0)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
