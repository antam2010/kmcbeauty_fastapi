"""add index shop.user_id and treatment_item.treatment_id

FK 필터/조인 정확성·견고성을 위한 최소 인덱스 추가 (SPEC-FIX-001 REQ-FIX-005).
- ix_shop_user_id: 유저별 샵 조회(get_user_shops/get_user_shop_by_id) FK 필터
- ix_treatment_item_treatment_id: 자동완료/목록 조인의 treatment_id FK 필터

Revision ID: a1b2c3d4e5f6
Revises: 1e1480804309
Create Date: 2026-07-02 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "1e1480804309"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_shop_user_id",
        "shop",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_treatment_item_treatment_id",
        "treatment_item",
        ["treatment_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_treatment_item_treatment_id", table_name="treatment_item")
    op.drop_index("ix_shop_user_id", table_name="shop")
