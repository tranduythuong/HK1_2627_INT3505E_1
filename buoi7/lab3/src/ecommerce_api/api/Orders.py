from flask_smorest import Blueprint
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload

from ecommerce_api.Extensions import db
from ecommerce_api.exceptions.AppException import NotFound, OutOfStock
from ecommerce_api.models.Order import Order
from ecommerce_api.models.OrderItem import OrderItem
from ecommerce_api.models.Product import Product
from ecommerce_api.schemas.Order import (
    OrderCreateSchema,
    OrderErrorSchema,
    OrderResponseSchema,
)


order_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/orders",
    description="Create and view orders.",
)


@order_bp.route("", methods=["POST"])
@order_bp.arguments(OrderCreateSchema)
@order_bp.response(201, OrderResponseSchema)
@order_bp.alt_response(404, schema=OrderErrorSchema, description="Product not found")
@order_bp.alt_response(409, schema=OrderErrorSchema, description="Insufficient stock")
def create_order(data):
    """Create an order with one or more distinct products."""
    product_ids = [item["product_id"] for item in data["items"]]
    products = db.session.scalars(
        select(Product).where(Product.id.in_(product_ids), Product.archived.is_(False))
    ).all()
    products_by_id = {product.id: product for product in products}
    missing_ids = set(product_ids) - products_by_id.keys()
    if missing_ids:
        raise NotFound(message=f"Product not found: {min(missing_ids)}.")

    order = Order()
    db.session.add(order)
    try:
        for item in data["items"]:
            product_id = item["product_id"]
            quantity = item["quantity"]
            result = db.session.execute(
                update(Product)
                .where(
                    Product.id == product_id,
                    Product.archived.is_(False),
                    Product.qty_in_stock >= quantity,
                )
                .values(qty_in_stock=Product.qty_in_stock - quantity)
            )
            if result.rowcount != 1:
                raise OutOfStock(message=f"Insufficient stock for product {product_id}.")
            order.items.append(
                OrderItem(
                    product_id=product_id,
                    quantity=quantity,
                    unit_price_cents=products_by_id[product_id].price_cents,
                )
            )
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return db.session.scalar(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items).joinedload(OrderItem.product))
    )


@order_bp.route("/<int:order_id>", methods=["GET"])
@order_bp.response(200, OrderResponseSchema)
@order_bp.alt_response(404, schema=OrderErrorSchema, description="Order not found")
def get_order(order_id):
    """Get an order and its items and products with a bounded query count."""
    order = db.session.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).joinedload(OrderItem.product))
    )
    if order is None:
        raise NotFound(message="Order not found.")
    return order
