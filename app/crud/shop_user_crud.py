from sqlalchemy.orm import Session, joinedload

from app.models.shop_user import ShopUser


def get_shop_user(db: Session, shop_id: int, user_id: int) -> ShopUser:
    """나의 샵 유저 정보 조회.

    Args:
        db (Session): _description_
        shop_id (int): _description_
        user_id (int): _description_

    Returns:
        ShopUser: _description_

    """
    return db.query(ShopUser).filter_by(shop_id=shop_id, user_id=user_id).first()


def create_shop_user(db: Session, shop_user_data: ShopUser) -> ShopUser:
    """샵 유저 생성.

    Args:
        db (Session): Database session.
        shop_user_data (ShopUser): Shop user data to create.

    Returns:
        ShopUser: The created shop user.

    """
    db.add(shop_user_data)
    db.flush()
    return shop_user_data


def get_shop_users_by_shop_id(db: Session, shop_id: int) -> list[ShopUser]:
    """팀 샵 유저의 샵 ID 목록 조회.

    Args:
        db (Session): Database session.
        shop_id (int): The ID of the shop to filter by.

    Returns:
        list[ShopUser]: List of shop users associated with the given shop ID.

    """
    return (
        db.query(ShopUser)
        .options(joinedload(ShopUser.user))
        .filter(ShopUser.shop_id == shop_id)
        .all()
    )
