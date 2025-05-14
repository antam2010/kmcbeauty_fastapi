from app.schemas.base import BaseResponseModel


class LoginResponse(BaseResponseModel):
    access_token: str
    refresh_token: str
    token_type: str | None = "bearer"
