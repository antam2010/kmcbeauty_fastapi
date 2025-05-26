from typing import ClassVar

from pydantic import Field

from app.schemas.mixin.base import BaseResponseModel
from app.schemas.user import UserResponse


class ShopUserBase(BaseResponseModel):
    shop_id: int = Field(..., description="샵 ID")
    user_id: int = Field(..., description="유저 ID")
    is_primary_owner: int = Field(..., description="대표 원장 여부 (1=대표, 0=아님)")


class ShopUserCreate(ShopUserBase):
    pass


class ShopUserUpdate(BaseResponseModel):
    is_primary_owner: int | None = Field(
        None,
        description="대표 원장 여부 (1=대표, 0=아님)",
    )


class ShopUserInDBBase(ShopUserBase):
    id: int = Field(..., description="PK")

    model_config: ClassVar[dict] = {
        "from_attributes": True,
    }


class ShopUserResponse(ShopUserInDBBase):
    pass


class ShopUserUserResponse(ShopUserBase):
    user: UserResponse = Field(..., description="유저 정보")
    model_config: ClassVar[dict] = {
        "from_attributes": True,
    }
