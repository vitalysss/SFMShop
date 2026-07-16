"""remove legacy order user name

Revision ID: 04a4d5efaead
Revises: b241b0c55db1
Create Date: 2026-07-16 18:55:47.927963

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "04a4d5efaead"
down_revision: Union[str, Sequence[str], None] = "b241b0c55db1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove the legacy user_name column."""

    op.drop_column(
        "orders",
        "user_name",
    )


def downgrade() -> None:
    """Restore the legacy user_name column."""

    op.add_column(
        "orders",
        sa.Column(
            "user_name",
            sa.String(length=100),
            nullable=True,
        ),
    )
