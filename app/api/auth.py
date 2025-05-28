from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import REFRESH_TOKEN_EXPIRE_SECONDS
from app.database import get_db
from app.docs.common_responses import COMMON_ERROR_RESPONSES
from app.schemas.auth import LoginResponse
from app.services.auth_service import (
    authenticate_user_service,
    generate_tokens,
    logout_user,
    refresh_access_token,
)

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post(
    "/login",
    summary="사용자 로그인",
    description=(
        "이메일(username)과 비밀번호(password)를 입력하여 JWT 토큰을 발급받습니다."
    ),
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: COMMON_ERROR_RESPONSES[
            status.HTTP_401_UNAUTHORIZED
        ],
    },
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    user = authenticate_user_service(db, form_data.username, form_data.password)
    access_token, refresh_token = generate_tokens(user)

    response_data = LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    response = JSONResponse(content=response_data.model_dump())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="None",  # Lax, Strict, None
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    return response


@router.post(
    "/refresh",
    summary="엑세스 토큰 재발급",
    description="리프레시 토큰을 쿠키로 받아 새로운 엑세스 토큰을 발급합니다.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "리프레시 토큰이 유효하지 않음"},
    },
)
def refresh_token_handler(
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    new_access_token, new_refresh_token = refresh_access_token(db, request)

    response_data = LoginResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
    response = JSONResponse(content=response_data.model_dump())
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="None",  # Lax, Strict, None
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    return response


@router.post(
    "/logout",
    summary="사용자 로그아웃",
    description="로그아웃 시 쿠키 제거 및 레디스에서 리프레시 토큰 삭제",
    status_code=status.HTTP_200_OK,
)
def logout(request: Request) -> JSONResponse:
    token = request.cookies.get("refresh_token")
    result = logout_user(token)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "로그아웃 성공",
            "token": token,
            "result": result,
        },
    )
    response.delete_cookie("refresh_token", path="/")
    return response
