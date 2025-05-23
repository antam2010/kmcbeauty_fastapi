"""update phonebook uniq_index

Revision ID: 5b57aeb86c24
Revises: 4eee4a776386
Create Date: 2025-04-17 15:18:31.508783

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b57aeb86c24"
down_revision: Union[str, None] = "4eee4a776386"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("ix_shop_id", "phonebook", ["shop_id"])
    op.drop_index("uq_shop_id_phone_number", table_name="phonebook")
    op.drop_table_comment(
        "phonebook", existing_comment="전화번호부 테이블", schema=None
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table_comment(
        "phonebook", "전화번호부 테이블", existing_comment=None, schema=None
    )
    op.create_index(
        "uq_shop_id_phone_number", "phonebook", ["shop_id", "phone_number"], unique=True
    )
    op.drop_index("ix_shop_id", table_name="phonebook")
    # ### end Alembic commands ###
