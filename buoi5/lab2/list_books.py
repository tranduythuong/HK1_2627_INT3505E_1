
from flask import Flask, request, jsonify
import base64
import json
from functools import cmp_to_key

app = Flask(__name__)

# =========================================================
# 1. DATA
# Thay BOOKS bằng dữ liệu hiện có của Lab 1 nếu đã có.
# =========================================================

BOOKS = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "genre": "Programming",
        "published_year": 2008
    },
    {
        "id": 2,
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "genre": "Programming",
        "published_year": 1999
    },
    {
        "id": 3,
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "published_year": 1965
    },
    {
        "id": 4,
        "title": "1984",
        "author": "George Orwell",
        "genre": "Fiction",
        "published_year": 1949
    },
    {
        "id": 5,
        "title": "Animal Farm",
        "author": "George Orwell",
        "genre": "Fiction",
        "published_year": 1945
    },
    {
        "id": 6,
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "genre": "Programming",
        "published_year": 2019
    },
    {
        "id": 7,
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "genre": "Fantasy",
        "published_year": 1937
    },
    {
        "id": 8,
        "title": "Harry Potter",
        "author": "J. K. Rowling",
        "genre": "Fantasy",
        "published_year": 1997
    },
    {
        "id": 9,
        "title": "Foundation",
        "author": "Isaac Asimov",
        "genre": "Science Fiction",
        "published_year": 1951
    },
    {
        "id": 10,
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "genre": "Fiction",
        "published_year": 1988
    },
]


# =========================================================
# 2. CONFIGURATION
# =========================================================

SORT_FIELDS = {
    "id",
    "title",
    "author",
    "genre",
    "published_year",
}

DEFAULT_SORT = [("id", "asc")]




def parse_sort(raw_sort):
    if not raw_sort:
        return DEFAULT_SORT.copy()

    sort_keys = []

    for item in raw_sort.split(","):
        parts = item.strip().split(":")

        if len(parts) != 2:
            raise ValueError(
                "sort must use field:asc or field:desc"
            )

        field = parts[0].strip()
        direction = parts[1].strip().lower()

        if field not in SORT_FIELDS:
            raise ValueError(
                f"Unsupported sort field: {field}"
            )

        if direction not in ("asc", "desc"):
            raise ValueError(
                "Sort direction must be asc or desc"
            )

        if any(existing == field for existing, _ in sort_keys):
            raise ValueError(
                f"Duplicate sort field: {field}"
            )

        sort_keys.append((field, direction))

    # Thêm khóa phụ để thứ tự ổn định.
    if "id" not in [field for field, _ in sort_keys]:
        sort_keys.append(("id", "asc"))

    return sort_keys


# =========================================================
# 4. COMPARE VALUES AND BOOKS
# =========================================================

def normalize_value(value):
    if isinstance(value, str):
        return value.casefold()
    return value


def compare_values(a, b):
    if a is None and b is None:
        return 0

    if a is None:
        return -1

    if b is None:
        return 1

    a = normalize_value(a)
    b = normalize_value(b)

    return (a > b) - (a < b)


def compare_books(book_a, book_b, sort_keys):
    for field, direction in sort_keys:
        result = compare_values(
            book_a.get(field),
            book_b.get(field)
        )

        if result != 0:
            if direction == "desc":
                result = -result

            return result

    return 0


def compare_book_to_cursor(book, cursor_values, sort_keys):
    for index, (field, direction) in enumerate(sort_keys):
        result = compare_values(
            book.get(field),
            cursor_values[index]
        )

        if result != 0:
            if direction == "desc":
                result = -result

            return result

    return 0


# =========================================================
# 5. CURSOR ENCODING / DECODING
# =========================================================

def encode_cursor(book, sort_keys):
    values = [
        book.get(field)
        for field, _ in sort_keys
    ]

    raw = json.dumps(
        values,
        ensure_ascii=False
    ).encode("utf-8")

    return base64.urlsafe_b64encode(
        raw
    ).decode("ascii")


def decode_cursor(cursor):
    try:
        raw = base64.b64decode(
            cursor.encode("ascii"),
            altchars=b"-_",
            validate=True
        )

        values = json.loads(raw.decode("utf-8"))

        if not isinstance(values, list):
            raise ValueError("Cursor must contain a list")

        return values

    except (
        ValueError,
        TypeError,
        UnicodeError,
        json.JSONDecodeError
    ):
        raise ValueError("Invalid cursor")


# =========================================================
# 6. LIST BOOKS
# =========================================================

@app.get("/books")
def list_books():
    try:
        # ----- Read query parameters -----

        strategy = request.args.get(
            "strategy", "offset"
        ).strip().lower()

        if strategy not in ("offset", "cursor"):
            raise ValueError(
                "strategy must be offset or cursor"
            )

        try:
            limit = int(request.args.get("limit", "10"))
        except (ValueError, TypeError):
            raise ValueError("limit must be an integer")

        if not 1 <= limit <= 100:
            raise ValueError(
                "limit must be between 1 and 100"
            )

        sort_keys = parse_sort(
            request.args.get("sort")
        )

        # ----- 1. FILTER -----

        books = BOOKS.copy()

        genre = request.args.get("genre")

        if genre is not None:
            genre = genre.strip()

            if not genre:
                raise ValueError(
                    "genre must not be empty"
                )

            books = [
                book for book in books
                if str(book.get("genre", "")).casefold()
                == genre.casefold()
            ]

        # ----- 2. SORT -----

        books.sort(
            key=cmp_to_key(
                lambda a, b: compare_books(
                    a, b, sort_keys
                )
            )
        )

        # ----- 3A. OFFSET PAGINATION -----

        if strategy == "offset":
            try:
                offset = int(
                    request.args.get("offset", "0")
                )
            except (ValueError, TypeError):
                raise ValueError(
                    "offset must be an integer"
                )

            if offset < 0:
                raise ValueError(
                    "offset must be non-negative"
                )

            total = len(books)

            page = books[offset:offset + limit]

            return jsonify({
                "data": page,
                "pagination": {
                    "strategy": "offset",
                    "limit": limit,
                    "offset": offset,
                    "total": total,
                    "has_next": (
                        offset + len(page) < total
                    ),
                }
            }), 200

        # ----- 3B. CURSOR PAGINATION -----

        cursor = request.args.get("cursor")

        if cursor is not None:
            cursor_values = decode_cursor(cursor)

            if len(cursor_values) != len(sort_keys):
                raise ValueError(
                    "Cursor does not match sort fields"
                )

            # Chỉ lấy các bản ghi đứng sau cursor
            # theo đúng thứ tự sort hiện tại.
            books = [
                book for book in books
                if compare_book_to_cursor(
                    book,
                    cursor_values,
                    sort_keys
                ) > 0
            ]

        # Lấy limit + 1 để xác định còn trang tiếp theo không.
        candidates = books[:limit + 1]
        has_next = len(candidates) > limit
        page = candidates[:limit]

        next_cursor = None

        if has_next and page:
            next_cursor = encode_cursor(
                page[-1],
                sort_keys
            )

        return jsonify({
            "data": page,
            "pagination": {
                "strategy": "cursor",
                "limit": limit,
                "next_cursor": next_cursor,
                "has_next": has_next,
            }
        }), 200

    except ValueError as error:
        return jsonify({
            "title": "Bad Request",
            "status": 400,
            "detail": str(error),
        }), 400

    except (TypeError, KeyError):
        return jsonify({
            "title": "Bad Request",
            "status": 400,
            "detail": "Invalid query parameters",
        }), 400


# =========================================================
# 7. RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
