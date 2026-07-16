"""remove legacy order user name trigger

Revision ID: 59b9094c7819
Revises: 04a4d5efaead
Create Date: 2026-07-16 21:15:32.546741

"""

from alembic import op

revision = "59b9094c7819"
down_revision = "04a4d5efaead"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove the obsolete order user name trigger."""

    op.execute(
        """
        DROP TRIGGER IF EXISTS
        trg_set_order_user_name
        ON orders
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS
        set_order_user_name()
        """
    )


def downgrade() -> None:
    """The obsolete trigger is not restored."""
