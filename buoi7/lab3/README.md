# Ecommerce API

## Run with Docker

From the repository root:

```sh
docker compose -f buoi7/lab3/docker-compose.yml up --build
```

The API listens on port `5000`. Docker Compose stores the SQLite database in a
named volume and applies database migrations when the container starts.

## Main routes

- `POST /orders` creates an order from an `items` array.
- `GET /orders/<order_id>` returns the order and its items.
- `GET /healthz` reports whether the app process is running.
- `GET /ready` checks whether the database is reachable.

## Run tests

From the repository root:

```sh
python -m pytest buoi7/lab3/tests
```

For local development, set `DATABASE_URL` to a SQLAlchemy database URL. If it
is omitted, Flask uses its default SQLite database in the instance directory.
