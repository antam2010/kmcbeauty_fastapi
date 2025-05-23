"""create refresh model

Revision ID: eee7baaeea97
Revises: 26c3cb6bca80
Create Date: 2025-05-02 15:18:26.356925

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eee7baaeea97"
down_revision: Union[str, None] = "26c3cb6bca80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, comment="리프레시 토큰 ID"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="사용자 ID"),
        sa.Column("token", sa.Text(), nullable=False, comment="리프레시 토큰"),
        sa.Column("expired_at", sa.DateTime(), nullable=False, comment="만료일시"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="생성일시",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="수정일시",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refresh_tokens_id"), "refresh_tokens", ["id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("ix_shop_id", "phonebook", ["shop_id"], unique=False)
    op.drop_index(op.f("ix_refresh_tokens_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    # ### end Alembic commands ###
