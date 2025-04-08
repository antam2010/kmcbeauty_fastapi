from pydantic import BaseModel, EmailStr, Field

from app.enum.role import UserRole


class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="이름은 3자 이상 50자 이하입니다.",
        examples=["홍길동"],
    )
    email: EmailStr = Field(..., description="유효한 이메일 주소여야 합니다.")
    password: str = Field(
        ...,
        min_length=4,
        description="비밀번호는 4자 이상입니다.",
        examples=["password123"],
    )
    role: UserRole = Field(..., description="유저 권한(ADMIN, MASTER, MANAGER)")


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = Field(None, description="유효한 이메일 주소여야 합니다.")
    password: str | None = Field(None, min_length=4)


class UserUpdateToken(BaseModel):
    token: str = Field(..., description="휴대폰 토큰.")


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True
