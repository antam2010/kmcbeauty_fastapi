from pydantic import BaseModel, EmailStr, Field

from app.enum.role import UserRole


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="유효한 이메일 주소여야 합니다.")
    password: str = Field(..., min_length=8)
    role: UserRole = Field(..., description="유저 권한(ADMIN, MASTER, MANAGER)")
    token: str | None = Field(None, description="휴대폰 토큰.")


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True
