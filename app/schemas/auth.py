from app.schemas.base import BaseResponseModel
class LoginResponse(BaseResponseModel):
    access_token: str
    token_type: str = "bearer"
