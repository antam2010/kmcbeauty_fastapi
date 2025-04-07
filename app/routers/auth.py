from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.model.user import User
from app.schemas.auth import LoginResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    summary="사용자 로그인",
    description="이메일(username)과 비밀번호(password)를 입력하여 JWT 토큰을 발급받습니다.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "로그인 성공, JWT 토큰 반환"},
        401: {"description": "로그인 실패 - 인증 정보 불일치"},
    },
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}
