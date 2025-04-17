from pydantic import BaseModel, EmailStr, Field

from app.enum.role import UserRole


# 유저 생성 요청 스키마
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="이름")
    email: EmailStr = Field(..., description="유효한 이메일 주소")
    password: str = Field(..., min_length=4, description="비밀번호")
    role: UserRole = Field(..., description="유저 권한")


# 유저 수정 요청 스키마
class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50, description="이름")
    email: EmailStr | None = Field(None, description="유효한 이메일 주소")
    password: str | None = Field(None, min_length=4, description="비밀번호")


# 유저 토큰 수정 요청 스키마 (ex: FCM 토큰 등)
class UserUpdateToken(BaseModel):
    token: str = Field(..., description="휴대폰 토큰")


# 유저 조회 응답 스키마
class UserResponse(BaseModel):
    id: int = Field(..., description="유저 고유 ID")
    name: str = Field(..., description="이름")
    email: EmailStr = Field(..., description="이메일 주소")
    role: UserRole = Field(..., description="유저 권한")

    model_config = {"from_attributes": True}


# 이메일 중복 체크 응답 스키마
class UserEmailCheckResponse(BaseModel):
    exists: bool = Field(..., description="이메일 중복 여부")
    message: str | None = Field(None, description="메시지")

    model_config = {"from_attributes": True}
