from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    price: float

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price}


class ProductRepository:
    """In-memory product storage for this lab."""

    def __init__(self):
        self._products = {}
        self._next_id = 1

    def list(self):
        return list(self._products.values())

    def get(self, product_id):
        return self._products.get(product_id)

    def create(self, name, price):
        product = Product(id=self._next_id, name=name, price=price)
        self._products[product.id] = product
        self._next_id += 1
        return product

    def update(self, product, name, price):
        product.name = name
        product.price = price
        return product

    def delete(self, product):
        del self._products[product.id]


products = ProductRepository()
