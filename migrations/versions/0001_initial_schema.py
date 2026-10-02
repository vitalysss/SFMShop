"""create initial database schema

Revision ID: 0001_initial_schema
Revises:
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=100),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "balance",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP"
            ),
        ),
    )

    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP"
            ),
        ),
    )

    op.create_table(
        "orders",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "user_name",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "total",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text(
                "CURRENT_TIMESTAMP"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="orders_user_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="orders_product_id_fkey",
        ),
    )

    op.create_index(
        "idx_orders_product_id",
        "orders",
        ["product_id"],
    )

    op.create_table(
        "reviews",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "review_text",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "rating",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_name",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text(
                "CURRENT_TIMESTAMP"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_index(
        "idx_orders_product_id",
        table_name="orders",
    )
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("users")