"""update order schema

Revision ID: b241b0c55db1
Revises:
Create Date: 2026-07-16 17:59:55.761572

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b241b0c55db1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        """
        UPDATE products
        SET quantity = 0
        WHERE quantity IS NULL
        """
    )

    op.alter_column(
        "products",
        "quantity",
        new_column_name="stock",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.execute(
        """
        UPDATE orders
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.alter_column(
        "orders",
        "created_at",
        new_column_name="order_date",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )

    op.add_column(
        "orders",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
    )

    op.create_table(
        "order_items",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "order_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
    )

    op.execute(
        """
        INSERT INTO order_items (
            order_id,
            product_id,
            quantity,
            price
        )
        SELECT
            id,
            product_id,
            1,
            total
        FROM orders
        WHERE product_id IS NOT NULL
        """
    )

    op.create_index(
        "idx_order_items_product_id",
        "order_items",
        ["product_id"],
    )

    op.create_index(
        "idx_orders_date",
        "orders",
        ["order_date"],
    )

    op.drop_constraint(
        "orders_product_id_fkey",
        "orders",
        type_="foreignkey",
    )

    op.drop_index(
        "idx_orders_product_id",
        table_name="orders",
    )

    op.drop_column(
        "orders",
        "product_id",
    )

    op.alter_column(
        "orders",
        "status",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "orders",
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE orders
        SET product_id = source.product_id
        FROM (
            SELECT DISTINCT ON (order_id)
                order_id,
                product_id
            FROM order_items
            ORDER BY order_id, id
        ) AS source
        WHERE orders.id = source.order_id
        """
    )

    op.create_foreign_key(
        "orders_product_id_fkey",
        "orders",
        "products",
        ["product_id"],
        ["id"],
    )

    op.create_index(
        "idx_orders_product_id",
        "orders",
        ["product_id"],
    )

    op.drop_index(
        "idx_orders_date",
        table_name="orders",
    )

    op.drop_index(
        "idx_order_items_product_id",
        table_name="order_items",
    )

    op.drop_table(
        "order_items",
    )

    op.drop_column(
        "orders",
        "status",
    )

    op.alter_column(
        "orders",
        "order_date",
        new_column_name="created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )

    op.alter_column(
        "products",
        "stock",
        new_column_name="quantity",
        existing_type=sa.Integer(),
        nullable=False,
    )
