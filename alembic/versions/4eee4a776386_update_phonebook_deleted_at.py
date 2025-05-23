"""update phonebook deleted_at

Revision ID: 4eee4a776386
Revises: 55b0f3aef89c
Create Date: 2025-04-17 15:03:43.569421

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4eee4a776386"
down_revision: Union[str, None] = "55b0f3aef89c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "phonebook",
        sa.Column("deleted_at", sa.DateTime(), nullable=True, comment="삭제일시"),
    )
    op.alter_column(
        "phonebook",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "phonebook",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="수정일시",
        existing_comment="수정일",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "shop",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "shop",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="수정일시",
        existing_comment="수정일",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="수정일시",
        existing_comment="수정일",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.add_column(
        "treatment_item",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="수정일시",
        ),
    )
    op.alter_column(
        "treatment_item",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu",
        "deleted_at",
        existing_type=mysql.DATETIME(),
        comment="삭제일시",
        existing_comment="삭제일시 (soft delete)",
        existing_nullable=True,
    )
    op.alter_column(
        "treatment_menu",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="수정일시",
        existing_comment="수정일",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu_detail",
        "deleted_at",
        existing_type=mysql.DATETIME(),
        comment="삭제일시",
        existing_comment="삭제일시 (soft delete)",
        existing_nullable=True,
    )
    op.alter_column(
        "treatment_menu_detail",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu_detail",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="수정일시",
        existing_comment="수정일",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.add_column(
        "users",
        sa.Column("deleted_at", sa.DateTime(), nullable=True, comment="삭제일시"),
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="생성일시",
        existing_comment="생성일",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=False,
        comment="수정일시",
        existing_comment="수정일",
        existing_server_default=sa.text(
            "current_timestamp() ON UPDATE current_timestamp()"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="수정일",
        existing_comment="수정일시",
        existing_server_default=sa.text(
            "current_timestamp() ON UPDATE current_timestamp()"
        ),
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="생성일",
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.drop_column("users", "deleted_at")
    op.alter_column(
        "treatment_menu_detail",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="수정일",
        existing_comment="수정일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu_detail",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu_detail",
        "deleted_at",
        existing_type=mysql.DATETIME(),
        comment="삭제일시 (soft delete)",
        existing_comment="삭제일시",
        existing_nullable=True,
    )
    op.alter_column(
        "treatment_menu",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="수정일",
        existing_comment="수정일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment_menu",
        "deleted_at",
        existing_type=mysql.DATETIME(),
        comment="삭제일시 (soft delete)",
        existing_comment="삭제일시",
        existing_nullable=True,
    )
    op.alter_column(
        "treatment_item",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.drop_column("treatment_item", "updated_at")
    op.alter_column(
        "treatment",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="수정일",
        existing_comment="수정일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "treatment",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "shop",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="수정일",
        existing_comment="수정일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "shop",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "phonebook",
        "updated_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        comment="수정일",
        existing_comment="수정일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.alter_column(
        "phonebook",
        "created_at",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_comment="생성일시",
        existing_server_default=sa.text("current_timestamp()"),
    )
    op.drop_column("phonebook", "deleted_at")
    # ### end Alembic commands ###
