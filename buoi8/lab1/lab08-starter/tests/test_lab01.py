"""Lab 1 API behavior and response-contract tests."""

from jsonschema import validate

from tools import get_book_schema


def test_get_books_empty_database_returns_empty_array(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.get_json() == []
    assert isinstance(response.get_json(), list)


def test_get_missing_book_returns_not_found(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_post_book_missing_title_returns_validation_error(client):
    response = client.post("/books", json={"author": "J.J. Geewax"})

    assert response.status_code == 400
    assert any(
        error["field"] == "title" for error in response.get_json()["errors"]
    )


def test_delete_book_then_get_returns_not_found(client, sample_book):
    delete_response = client.delete(f"/books/{sample_book}")
    get_response = client.get(f"/books/{sample_book}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
    assert get_response.get_json()["code"] == "NOT_FOUND"


def test_response_extra_field_blocked(client, sample_book):
    response = client.get(f"/books/{sample_book}")

    assert response.status_code == 200
    payload = response.get_json()
    assert "password_hash" not in payload
    validate(instance=payload, schema=get_book_schema())