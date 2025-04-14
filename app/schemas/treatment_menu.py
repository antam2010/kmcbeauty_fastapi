from datetime import datetime

from pydantic import BaseModel, Field


# 시술 메뉴 상세 생성
class TreatmentMenuDetailCreate(BaseModel):
    name: str = Field(..., description="시술 메뉴 상세 이름", max_length=255)
    duration_min: int = Field(..., description="시술 소요 시간(분)", gt=0)
    base_price: int = Field(..., description="기본 가격", gt=0)

    class Config:
        orm_mode = True

# 시술 메뉴 상세 조회 응답
class TreatmentMenuDetailResponse(BaseModel):
    id: int = Field(..., description="시술 메뉴 상세 ID")
    menu_id: int = Field(..., description="시술 메뉴 ID")
    name: str = Field(..., description="시술 메뉴 상세 이름", max_length=255)
    duration_min: int = Field(..., description="시술 소요 시간(분)", gt=0)
    base_price: int = Field(..., description="기본 가격", gt=0)
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    class Config:
        orm_mode = True

        
# 시술 메뉴 생성
class TreatmentMenuCreate(BaseModel):
    name : str = Field(..., description="시술 메뉴 이름", max_length=255)
    class Config:
        orm_mode = True

# 시술 메뉴 생성 응답
class TreatmentMenuCreateResponse(BaseModel):
    id: int = Field(..., description="시술 메뉴 ID")
    name: str = Field(..., description="시술 메뉴 이름", max_length=255)
    created_at: datetime = Field(..., description="생성일")
    class Config:
        orm_mode = True

######################################################################################################################################################################################

# 메뉴 조회 파라미터
class TreatmentMenuListRequest(BaseModel):
    name: str | None = Field(
        None, description="시술 메뉴 이름", max_length=255
    )
    class Config:
        orm_mode = True

# 메뉴 조회 응답
class TreatmentMenuResponse(BaseModel):
    id: int = Field(..., description="시술 메뉴 ID")
    user_id: int = Field(..., description="사용자 ID")
    name: str = Field(..., description="시술 메뉴 이름", max_length=255)
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")
    details: list[TreatmentMenuDetailResponse] = Field(
        [], description="시술 메뉴 상세 목록"
    )
    class Config:
        orm_mode = True