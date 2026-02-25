"""add user onboarding_completed

Revision ID: a1b2c3d4e5f6
Revises: 74b975586598
Create Date: 2025-02-25 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "74b975586598"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "onboarding_completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.execute(sa.text('UPDATE "user" SET onboarding_completed = true'))


def downgrade() -> None:
    op.drop_column("user", "onboarding_completed")
