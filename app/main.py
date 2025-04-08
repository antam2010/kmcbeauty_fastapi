import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 추가할 라우터
from app.api import auth, user, phonebook, treatment, treatment_menu
from app.core.config import APP_ENV

# 로그 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),  # 로그 파일
        logging.StreamHandler(),  # 콘솔 출력
    ],
)

# 환경별 로그 레벨 설정
if APP_ENV == "local":
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
elif APP_ENV == "production":
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)


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