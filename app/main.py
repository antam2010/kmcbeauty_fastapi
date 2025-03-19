from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import logging
import time

# 추가할 라우터
from app.routers import user

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI 앱 생성
app = FastAPI(
    title="FastAPI 프로젝트",
    description="이 프로젝트는 FastAPI로 개발된 API 서비스입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정 (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안 강화하려면 특정 도메인만 허용)
    allow_credentials=True,  # 쿠키 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 요청 시간 측정 미들웨어
@app.middleware("http")
async def request_timer_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logging.info(f"⏱️ {request.method} {request.url.path} - {duration:.4f}s")
    return response

# 유효성 검사 예외 처리
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "입력 데이터가 유효하지 않습니다.", "errors": exc.errors()},
    )

# 헬스체크 엔드포인트 (서버 상태 확인)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "API 서버가 정상 동작 중입니다."}

# 사용자 관련 API 라우터 등록
app.include_router(user.router)
