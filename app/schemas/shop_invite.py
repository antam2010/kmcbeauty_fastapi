from datetime import datetime
from typing import ClassVar

from app.schemas.base import BaseResponseModel


class ShopInviteResponse(BaseResponseModel):
    shop_id: int
    invite_code: str
    expired_at: datetime
    model_config: ClassVar[dict] = {
        "from_attributes": True,
    }
