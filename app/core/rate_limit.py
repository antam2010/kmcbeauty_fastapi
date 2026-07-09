"""애플리케이션 전역 rate limiter 정의.

slowapi Limiter 를 별도 모듈로 분리하여 main.py 와 라우터(api/auth.py) 간
순환 참조 없이 공유한다. IP(get_remote_address) 기준으로 제한한다.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# IP 기반 rate limiter. 로그인 등 인증 엔드포인트 보호에 사용한다.
limiter = Limiter(key_func=get_remote_address)
