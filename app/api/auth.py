from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.database import get_db
from app.schemas.auth import LoginResponse
from app.services.auth_service import (
    authenticate_user,
    generate_tokens,
    logout_user,
    refresh_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    summary="사용자 로그인",
    description="이메일(username)과 비밀번호(password)를 입력하여 JWT 토큰을 발급받습니다.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> JSONResponse:
    user = authenticate_user(db, form_data.username, form_data.password)
    access_token, refresh_token = generate_tokens(db, user)

    max_age = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # 초 단위

    # Swagger에서는 response_model 기준으로 문서화
    response_data = LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    # 실제 응답은 쿠키 포함하여 JSONResponse로 설정
    response = JSONResponse(content=response_data.model_dump())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=max_age,
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
    header_token: str | None = Header(default=None, alias="X-Refresh-Token"),
    db: Session = Depends(get_db),
) -> LoginResponse:
    new_access_token, refresh_token = refresh_access_token(request, db)

    return LoginResponse(
        access_token=new_access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    summary="사용자 로그아웃",
    description="로그아웃 시 엑세스 토큰과 리프레시 토큰을 모두 만료 처리합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "로그아웃 성공",
            "content": {"application/json": {"example": {"message": "로그아웃 성공"}}},
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "서버 오류",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
def logout(request: Request, db: Session = Depends(get_db)):
    # 1) 리프레시 토큰을 쿠키에서 꺼내서 DB에서 삭제
    token = request.cookies.get("refresh_token")
    if token:
        logout_user(db, token)

    # 2) 쿠키에서 리프레시 토큰 삭제
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "로그아웃 성공",
            "token": token,
        },
    )
    response.delete_cookie("refresh_token", path="/")
    return response
