"""Add COMPLETED to treatment_status enum

Revision ID: 47a0a034caff
Revises: 9fa616bc2c95
Create Date: 2025-05-26 16:28:13.067414

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "47a0a034caff"
down_revision: str | None = "9fa616bc2c95"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE treatment 
        MODIFY COLUMN status ENUM(
            'RESERVED',
            'VISITED',
            'CANCELLED',
            'NO_SHOW',
            'COMPLETED'
        ) NOT NULL COMMENT '예약 상태';
    """)


def downgrade() -> None:
    pass
