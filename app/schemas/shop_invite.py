from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel


class ShopInviteResponse(BaseModel):
    shop_id: int
    invite_code: str
    expired_at: datetime
    model_config: ClassVar[dict] = {
        "from_attributes": True,
    }
