from pydantic import BaseModel
from typing import Optional

# 사용자 생성 요청 데이터 (입력)
class UserCreate(BaseModel):
    name: str
    password: str
    token: Optional[str] = None

# 사용자 응답 데이터 (출력)
class UserResponse(BaseModel):
    id: int
    name: str
    token: Optional[str] = None

    class Config:
        from_attributes = True  # ORM 모델을 Pydantic 스키마로 변환할 때 필요
