from flask_smorest import Blueprint
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from ecommerce_api.Extensions import db
from ecommerce_api.exceptions.AppException import Conflict, NotFound, OutOfStock
from ecommerce_api.models.Product import Product
from ecommerce_api.schemas.Product import (
    ProductCreateSchema,
    ProductErrorSchema,
    ProductPageSchema,
    ProductQuerySchema,
    ProductResponseSchema,
    ProductUpdateSchema,
    StockDecreaseSchema,
)

product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products",
    description="Create and manage products.",
)


def find_active_product(product_id):
    return Product.query.filter_by(id=product_id, archived=False).first()


@product_bp.route("/", methods=["POST"])
@product_bp.arguments(ProductCreateSchema)
@product_bp.response(201, ProductResponseSchema)
@product_bp.alt_response(409, schema=ProductErrorSchema, description="SKU already exists")
@product_bp.alt_response(422, schema=ProductErrorSchema, description="Request validation failed")
def create_product(product_data):
    """Create a product."""
    if Product.query.filter_by(sku=product_data["sku"]).first():
        raise Conflict(message="A product with this SKU already exists.")

    product = Product(**product_data)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict(message="A product with this SKU already exists.")
    return product


@product_bp.route("/", methods=["GET"])
@product_bp.arguments(ProductQuerySchema, location="query")
@product_bp.response(200, ProductPageSchema)
@product_bp.alt_response(422, schema=ProductErrorSchema, description="Invalid page or size")
def get_products(pagination_args):
    """List active products using pagination."""
    page = pagination_args["page"]
    size = pagination_args["size"]
    query = Product.query.filter_by(archived=False).order_by(Product.id)
    pagination = query.paginate(page=page, per_page=size, error_out=False)
    return {
        "items": pagination.items,
        "page": page,
        "size": size,
        "total": pagination.total,
    }


@product_bp.route("/<int:product_id>", methods=["GET"])
@product_bp.response(200, ProductResponseSchema)
@product_bp.alt_response(404, schema=ProductErrorSchema, description="Product not found")
def get_product(product_id):
    """Get an active product by ID."""
    product = find_active_product(product_id)
    if product is None:
        raise NotFound(message="Product not found.")
    return product


@product_bp.route("/<int:product_id>", methods=["PUT"])
@product_bp.arguments(ProductUpdateSchema)
@product_bp.response(200, ProductResponseSchema)
@product_bp.alt_response(404, schema=ProductErrorSchema, description="Product not found")
@product_bp.alt_response(409, schema=ProductErrorSchema, description="SKU already exists")
@product_bp.alt_response(422, schema=ProductErrorSchema, description="Request validation failed")
def update_product(product_data, product_id):
    """Update an active product."""
    product = find_active_product(product_id)
    if product is None:
        raise NotFound(message="Product not found.")

    if "sku" in product_data:
        duplicate = Product.query.filter(
            Product.sku == product_data["sku"], Product.id != product_id
        ).first()
        if duplicate:
            raise Conflict(message="A product with this SKU already exists.")

    for key, value in product_data.items():
        setattr(product, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict(message="A product with this SKU already exists.")
    return product


@product_bp.route("/<int:product_id>/reserve", methods=["POST"])
@product_bp.arguments(StockDecreaseSchema)
@product_bp.response(200, ProductResponseSchema)
@product_bp.alt_response(404, schema=ProductErrorSchema, description="Product not found")
@product_bp.alt_response(409, schema=ProductErrorSchema, description="Insufficient stock")
@product_bp.alt_response(422, schema=ProductErrorSchema, description="Request validation failed")
def decrease_stock(data, product_id):
    """Reserve stock by decreasing the available quantity."""
    product = find_active_product(product_id)
    if product is None:
        raise NotFound(message="Product not found.")

    amount = data["quantity"]
    result = db.session.execute(
        update(Product)
        .where(
            Product.id == product_id,
            Product.archived.is_(False),
            Product.qty_in_stock >= amount,
        )
        .values(qty_in_stock=Product.qty_in_stock - amount)
    )
    if result.rowcount != 1:
        db.session.rollback()
        raise OutOfStock(message="Insufficient stock for this decrease.")
    db.session.commit()
    return find_active_product(product_id)
