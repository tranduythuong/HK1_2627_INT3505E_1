from sqlalchemy import event

from ecommerce_api.Extensions import db
from ecommerce_api.models.Product import Product


def add_product(name, sku, stock=10, price=1250):
    product = Product(
        name=name,
        sku=sku,
        qty_in_stock=stock,
        price_cents=price,
        archived=False,
    )
    db.session.add(product)
    db.session.commit()
    return product


def test_post_order_creates_multiple_items_and_decreases_stock(client, app):
    with app.app_context():
        first = add_product("First", "FIRST-1", stock=5)
        second = add_product("Second", "SECOND-1", stock=4, price=2000)
        first_id, second_id = first.id, second.id
        payload = {
            "items": [
                {"product_id": first_id, "quantity": 2},
                {"product_id": second_id, "quantity": 1},
            ]
        }

    response = client.post("/orders", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert len(body["items"]) == 2
    assert {item["sku"] for item in body["items"]} == {"FIRST-1", "SECOND-1"}
    assert {item["unit_price_cents"] for item in body["items"]} == {1250, 2000}
    with app.app_context():
        assert db.session.get(Product, first_id).qty_in_stock == 3
        assert db.session.get(Product, second_id).qty_in_stock == 3


def test_get_order_eager_loads_items_and_products_without_n_plus_one(client, app):
    with app.app_context():
        first = add_product("First", "FIRST-2")
        second = add_product("Second", "SECOND-2")
        first_id, second_id = first.id, second.id
        response = client.post(
            "/orders",
            json={
                "items": [
                    {"product_id": first_id, "quantity": 1},
                    {"product_id": second_id, "quantity": 2},
                ]
            },
        )
        order_id = response.get_json()["id"]
        statement_count = 0

        def count_statements(_conn, _cursor, _statement, _parameters, _context, _many):
            nonlocal statement_count
            statement_count += 1

        event.listen(db.engine, "before_cursor_execute", count_statements)
        try:
            get_response = client.get(f"/orders/{order_id}")
        finally:
            event.remove(db.engine, "before_cursor_execute", count_statements)

    assert get_response.status_code == 200
    assert len(get_response.get_json()["items"]) == 2
    assert {item["product_name"] for item in get_response.get_json()["items"]} == {
        "First",
        "Second",
    }
    assert statement_count <= 2


def test_health_and_readiness_are_separate(client, app, monkeypatch):
    def fail_database(*_args, **_kwargs):
        raise RuntimeError("database unavailable")

    with app.app_context():
        monkeypatch.setattr(db.session, "execute", fail_database)

    assert client.get("/healthz").status_code == 200
    assert client.get("/ready").status_code == 503
