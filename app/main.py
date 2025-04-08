import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

# 추가할 라우터
from app.api import auth, user

# 로그 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# FastAPI 앱 생성
app = FastAPI(
    title="FastAPI 프로젝트",
    description="이 프로젝트는 FastAPI로 개발된 API 서비스입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,
)

# CORS 설정 (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안 강화하려면 특정 도메인만 허용)
    allow_credentials=True,  # 쿠키 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "유효성 검사 오류입니다.",
            "errors": exc.errors(),
        },
    )


# 헬스체크 엔드포인트 (서버 상태 확인)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "API 서버가 정상 동작 중입니다."}


# 사용자 관련 API 라우터 등록
app.include_router(user.router)
app.include_router(auth.router)
