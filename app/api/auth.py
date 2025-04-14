from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.database import get_db
from app.schemas.auth import LoginResponse
from app.services.auth_service import (
    authenticate_user,
    generate_tokens,
    refresh_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    summary="사용자 로그인",
    description="이메일(username)과 비밀번호(password)를 입력하여 JWT 토큰을 발급받습니다.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "로그인 실패 - 인증 정보 불일치"},
    },
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    access_token, refresh_token = generate_tokens(user)

    # Swagger에서는 response_model 기준으로 문서화
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
    }

    # 실제 응답은 쿠키 포함하여 JSONResponse로 설정
    response = JSONResponse(content=response_data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 초 단위
    )
    return response


@router.post(
    "/refresh",
    summary="엑세스 토큰 재발급",
    description="리프레시 토큰을 쿠키로 받아 새로운 엑세스 토큰을 발급합니다.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "리프레시 토큰이 유효하지 않음"},
    },
)
def refresh_token_handler(
    request: Request,
    db: Session = Depends(get_db),
):
    new_access_token = refresh_access_token(request, db)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
