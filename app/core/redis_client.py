import redis
from app.core.config import APP_ENV

if APP_ENV == "debug":
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
else:
    redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
