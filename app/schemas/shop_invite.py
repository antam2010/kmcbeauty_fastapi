from datetime import datetime

from app.schemas.base import BaseResponseModel


class ShopInviteResponse(BaseResponseModel):
    invite_code: str
    expired_at: datetime
