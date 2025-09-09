import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sentry_sdk import capture_exception
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api import auth, phonebook, shop, summary, treatment, treatment_menu, user
from app.core.config import APP_ENV, SENTRY_DSN
from app.core.logging import setup_logging
from app.core.sentry import init_sentry
from app.docs import api_change
from app.docs.tags_metadata import tags_metadata
from app.exceptions import CustomException

# 기타

# 로그 설정
setup_logging(app_env=APP_ENV)

# Sentry 설정
init_sentry(
    dsn=SENTRY_DSN,
    environment=APP_ENV,
    traces_sample_rate=0.2,
    profiles_sample_rate=0.0,
)


app = FastAPI(
    title="뷰티앱",
    description=(
        "이 프로젝트는 FastAPI로 개발된 API 서비스입니다.\n\n"
        "- 공통 미들웨어를 통해 사용자 인증 및 샵(상점) 선택 정보가 응답에 포함됩니다.\n"
        "- 액세스 토큰이 만료되었거나 리프레시 토큰이 없으면 `401 Unauthorized` 에러가 발생합니다.\n"
        "- 상점이 선택되지 않은 경우, 다음과 같은 에러 응답이 반환됩니다:\n"
        "  ```json\n"
        "  {\n"
        '    "detail": {\n'
        '      "code": "SHOP_NOT_SELECTED",\n'
        '      "message": "상점이 선택되지 않았습니다."\n'
        "    }\n"
        "  }\n\n"
        "- 각 API의 응답에는 도메인별 에러 코드가 포함되며, 코드 앞에는 도메인 이름(`{DOMAIN}`)이 붙습니다.\n"
        "  예: `USER_NOT_FOUND`, `TREATMENT_MENU_CONFLICT`, `PHONEBOOK_VALIDATION_ERROR` 등\n"
        "- `{DOMAIN}` 값은 각 API 설명 옆에 명시되어 있습니다."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=APP_ENV == "debug",
    openapi_tags=tags_metadata,
)


# CORS 설정 (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kmc2.daeho2.shop",
        "https://bueafit.vercel.app",
    ],
    allow_origin_regex=r"http://localhost(:\d+)?",
    allow_credentials=True,  # 쿠키 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


@app.middleware("http")
async def error_logger(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    try:
        # call_next 의 반환값을 Response 타입으로 명시
        response: Response = await call_next(request)
    except CustomException:
        raise
    except Exception as e:
        # 핸들되지 않은 예외(500) 일 때 스택트레이스 포함 로깅
        logging.exception(
            f"[UNHANDLED 500] {request.client.host} "
            f"{request.method} {request.url.path}",
        )
        # Sentry 전송
        capture_exception(e)
        raise
    return response


# 헬스체크 엔드포인트 (서버 상태 확인)
@app.get("/health", tags=["System"])
async def health_check() -> dict:
    return {"status": "ok", "message": "API 서버가 정상 동작 중입니다."}


# 사용자 관련 API 라우터 등록
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(phonebook.router)
app.include_router(treatment.router)
app.include_router(treatment_menu.router)
app.include_router(shop.router)
app.include_router(summary.router)
app.include_router(api_change.router)

# FastAPI Pagination 설정
add_pagination(app)
