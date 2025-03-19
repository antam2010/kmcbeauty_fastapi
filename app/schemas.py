from pydantic import BaseModel, Field
from typing import Optional

# 사용자 생성 요청 데이터 (입력)
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="이름은 3~50자 사이여야 합니다.")
    password: str = Field(..., min_length=8, description="비밀번호는 최소 8자 이상이어야 합니다.")
    token: Optional[str] = None

# 사용자 응답 데이터 (출력)
class UserResponse(BaseModel):
    id: int
    name: str
    token: Optional[str] = None

    class Config:
        from_attributes = True  # ORM 모델을 Pydantic 스키마로 변환할 때 필요
