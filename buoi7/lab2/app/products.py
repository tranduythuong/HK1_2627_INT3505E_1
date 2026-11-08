from connexion.exceptions import ProblemException

from .models import products


def api_root():
    return {
        "name": "Products API",
        "version": "v1",
        "docs": "/ui/",
        "openapi": "/openapi.json",
    }


def list_products():
    return [product.to_dict() for product in products.list()]


def create_product(body):
    product = products.create(name=body["name"], price=body["price"])
    return product.to_dict(), 201


def get_product(product_id):
    product = products.get(product_id)
    if product is None:
        raise ProblemException(
            status=404,
            title="Product not found",
            detail=f"No product exists with ID {product_id}.",
        )
    return product.to_dict()


def update_product(product_id, body):
    product = products.get(product_id)
    if product is None:
        raise ProblemException(
            status=404,
            title="Product not found",
            detail=f"No product exists with ID {product_id}.",
        )
    product = products.update(product, name=body["name"], price=body["price"])
    return product.to_dict()


def delete_product(product_id):
    product = products.get(product_id)
    if product is None:
        raise ProblemException(
            status=404,
            title="Product not found",
            detail=f"No product exists with ID {product_id}.",
        )
    products.delete(product)
    return {"message": "Product deleted successfully"}
