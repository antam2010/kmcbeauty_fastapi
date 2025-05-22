from pydantic import EmailStr, Field

from app.enum.role import UserRole
from app.schemas.base import BaseResponseModel


# 유저 생성 요청 스키마
class UserCreate(BaseResponseModel):
    name: str = Field(..., min_length=3, max_length=50, description="이름")
    email: EmailStr = Field(..., description="유효한 이메일 주소")
    password: str = Field(..., min_length=4, description="비밀번호")
    role: UserRole = Field(..., description="유저 권한")
    invite_code: str | None = Field(
        None,
        description="초대 코드",
        min_length=10,
        max_length=11,
    )


# 유저 수정 요청 스키마
class UserUpdate(UserCreate):
    name: str | None = Field(None, min_length=3, max_length=50, description="이름")
    email: EmailStr | None = Field(None, description="유효한 이메일 주소")
    password: str | None = Field(None, min_length=4, description="비밀번호")
    role: UserRole | None = Field(None, description="유저 권한")


# 유저 토큰 수정 요청 스키마 (ex: FCM 토큰 등)
class UserUpdateToken(BaseResponseModel):
    token: str = Field(..., description="휴대폰 토큰")


# 유저 조회 응답 스키마
# version 1.0.0
class UserResponse(BaseResponseModel):
    id: int = Field(..., description="유저 고유 ID")
    name: str = Field(..., description="이름")
    email: EmailStr = Field(..., description="이메일 주소")
    role: UserRole = Field(..., description="유저 권한")
    role_name: str = Field(None, description="유저 권한 이름(소스코드)")

    model_config = {"from_attributes": True}


# 이메일 중복 체크 응답 스키마
class UserEmailCheckResponse(BaseResponseModel):
    exists: bool = Field(..., description="이메일 중복 여부")
    message: str | None = Field(None, description="메시지")

    model_config = {"from_attributes": True}
