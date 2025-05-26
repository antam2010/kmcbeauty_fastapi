from pydantic import Field

from app.schemas.mixin.base import BaseResponseModel


class LoginResponse(BaseResponseModel):
    access_token: str
    refresh_token: str
    token_type: str | None = Field(default="bearer", description="토큰 타입")
