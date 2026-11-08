"""Sync products table with the current Product model.

Revision ID: 4c5d6e7f8091
Revises: 3b2c4d5e6f70
Create Date: 2026-11-08
"""
from alembic import op
import sqlalchemy as sa


revision = "4c5d6e7f8091"
down_revision = "3b2c4d5e6f70"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("products", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE products SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        )
        batch_op.alter_column(
            "description",
            existing_type=sa.String(length=255),
            type_=sa.String(length=2000),
            existing_nullable=True,
        )

    op.create_index("ix_products_archived", "products", ["archived"], unique=False)


def downgrade():
    op.drop_index("ix_products_archived", table_name="products")
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "description",
            existing_type=sa.String(length=2000),
            type_=sa.String(length=255),
            existing_nullable=True,
        )
        batch_op.drop_column("created_at")
