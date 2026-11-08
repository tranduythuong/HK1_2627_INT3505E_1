"""Migrate products to SKU, cents, stock, and archive fields.

Revision ID: 3b2c4d5e6f70
Revises: 99264d7e8453
Create Date: 2026-11-07
"""
from alembic import op
import sqlalchemy as sa


revision = "3b2c4d5e6f70"
down_revision = "99264d7e8453"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("products", sa.Column("sku", sa.String(length=32), nullable=True))
    op.add_column(
        "products",
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Preserve existing rows and convert the old currency-unit price to cents.
    op.execute("UPDATE products SET sku = 'LEGACY-' || id")
    op.execute("UPDATE products SET price = ROUND(price * 100)")

    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column("sku", existing_type=sa.String(length=32), nullable=False)
        batch_op.create_unique_constraint("uq_products_sku", ["sku"])
        batch_op.alter_column(
            "name", existing_type=sa.String(length=100), type_=sa.String(length=255),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "price", existing_type=sa.Float(), type_=sa.Integer(), new_column_name="price_cents",
            existing_nullable=False,
        )
        batch_op.alter_column(
            "quantity", existing_type=sa.Integer(), new_column_name="qty_in_stock",
            existing_nullable=False,
        )
        batch_op.create_check_constraint("ck_products_price_cents_nonnegative", "price_cents >= 0")
        batch_op.create_check_constraint("ck_products_qty_in_stock_nonnegative", "qty_in_stock >= 0")


def downgrade():
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint("ck_products_qty_in_stock_nonnegative", type_="check")
        batch_op.drop_constraint("ck_products_price_cents_nonnegative", type_="check")
        batch_op.alter_column(
            "qty_in_stock", existing_type=sa.Integer(), new_column_name="quantity",
            existing_nullable=False,
        )
        batch_op.alter_column(
            "price_cents", existing_type=sa.Integer(), type_=sa.Float(), new_column_name="price",
            existing_nullable=False,
        )
        batch_op.alter_column(
            "name", existing_type=sa.String(length=255), type_=sa.String(length=100),
            existing_nullable=False,
        )
        batch_op.drop_constraint("uq_products_sku", type_="unique")
        batch_op.drop_column("sku")
        batch_op.drop_column("archived")
