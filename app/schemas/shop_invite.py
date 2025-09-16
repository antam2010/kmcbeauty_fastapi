from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field


class ShopInviteResponse(BaseModel):
    shop_id: int
    invite_code: str
    expired_at: datetime
    model_config: ClassVar[dict] = {
        "from_attributes": True,
    }


class ShopInviteCreateRequest(BaseModel):
    expire_in: int | None = Field(
        default=60 * 60 * 24 * 7,
        description="초대코드 만료 기간(분 단위)",
    )
