from fastapi import FastAPI

# FastAPI의 라우터
from fastapi.middleware.cors import CORSMiddleware

# 라이브러리
from fastapi_pagination import add_pagination

# 추가할 라우터
from app.api import auth, phonebook, shop, treatment, treatment_menu, user

# config
from app.core.config import APP_ENV
from app.core.logging import setup_logging

# docs
from app.docs.tags_metadata import tags_metadata

# 로그 설정
setup_logging(app_env=APP_ENV)


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
    debug=True,
    openapi_tags=tags_metadata,
)


# CORS 설정 (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://kmc2.daeho2.shop",
        "http://localhost:5137",
        "http://localhost:8000",
    ],  # 모든 도메인 허용 (보안 강화하려면 특정 도메인만 허용)
    allow_credentials=True,  # 쿠키 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


# 헬스체크 엔드포인트 (서버 상태 확인)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "API 서버가 정상 동작 중입니다."}


# 사용자 관련 API 라우터 등록
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(phonebook.router)
app.include_router(treatment.router)
app.include_router(treatment_menu.router)
app.include_router(shop.router)

# FastAPI Pagination 설정
add_pagination(app)
