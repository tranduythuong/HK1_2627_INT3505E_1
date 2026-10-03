
from flask import Flask, request, jsonify
import base64

from buoi3.lab2.ErrorHandler import (
    ProblemError,
    register_error_handler
)


app = Flask(__name__)

# Đăng ký Error Handler
register_error_handler(app)


ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 500000},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 300000},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 700000},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 200000},
    {"id": 5, "customer_id": 102, "status": "paid", "total": 450000},
    {"id": 6, "customer_id": 104, "status": "pending", "total": 800000},
    {"id": 7, "customer_id": 101, "status": "paid", "total": 250000},
    {"id": 8, "customer_id": 105, "status": "paid", "total": 900000},
]


# =========================================================
# Cursor
# =========================================================

def encode_cursor(order_id):
    """Chuyển ID thành cursor."""
    data = str(order_id).encode()
    return base64.urlsafe_b64encode(data).decode()


def decode_cursor(cursor):
    """Giải mã cursor."""

    try:
        data = base64.urlsafe_b64decode(
            cursor.encode()
        ).decode()

        return int(data)

    except Exception:
        raise ProblemError(
            title="Invalid cursor",
            detail="The provided cursor is invalid.",
            status=400
        )


# =========================================================
# GET /orders
# =========================================================

@app.route("/orders", methods=["GET"])
def get_orders():

    # =====================================================
    # 1. Lấy query parameters
    # =====================================================

    cursor = request.args.get("cursor")
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")

    # -----------------------------------------------------
    # limit
    # -----------------------------------------------------

    try:
        limit = int(
            request.args.get("limit", 5)
        )

    except ValueError:
        raise ProblemError(
            title="Invalid limit",
            detail="limit must be an integer.",
            status=400
        )

    if limit <= 0:
        raise ProblemError(
            title="Invalid limit",
            detail="limit must be greater than 0.",
            status=400
        )

    # =====================================================
    # 2. Filter
    # =====================================================

    orders = ORDERS.copy()

    # -----------------------------------------------------
    # Filter theo status
    # -----------------------------------------------------

    if status:
        orders = [
            order
            for order in orders
            if order["status"] == status
        ]

    # -----------------------------------------------------
    # Filter theo customer_id
    # -----------------------------------------------------

    if customer_id:

        try:
            customer_id = int(customer_id)

        except ValueError:
            raise ProblemError(
                title="Invalid customer_id",
                detail="customer_id must be an integer.",
                status=400
            )

        orders = [
            order
            for order in orders
            if order["customer_id"] == customer_id
        ]

    # =====================================================
    # 3. Sort
    # =====================================================

    sort = request.args.get("sort", "id")

    reverse = False

    # sort=-total
    if sort.startswith("-"):
        sort = sort[1:]
        reverse = True

    allowed_sort = [
        "id",
        "total",
        "customer_id"
    ]

    if sort not in allowed_sort:

        raise ProblemError(
            title="Invalid sort",
            detail=(
                "sort must be one of: "
                + ", ".join(allowed_sort)
            ),
            status=400
        )

    orders.sort(
        key=lambda order: order[sort],
        reverse=reverse
    )

    # =====================================================
    # 4. Cursor pagination
    # =====================================================

    if cursor:

        cursor_id = decode_cursor(cursor)

        # -------------------------------------------------
        # sort tăng dần theo id
        # -------------------------------------------------

        if not reverse and sort == "id":

            orders = [
                order
                for order in orders
                if order["id"] > cursor_id
            ]

        # -------------------------------------------------
        # sort giảm dần theo id
        # -------------------------------------------------

        elif reverse and sort == "id":

            orders = [
                order
                for order in orders
                if order["id"] < cursor_id
            ]

    # =====================================================
    # 5. Pagination
    # =====================================================

    has_more = len(orders) > limit

    page = orders[:limit]

    # =====================================================
    # 6. Tạo next_cursor
    # =====================================================

    next_cursor = None

    if has_more:

        next_cursor = encode_cursor(
            page[-1]["id"]
        )

    # =====================================================
    # 7. Sparse fieldsets
    # =====================================================

    fields = request.args.get("fields")

    if fields:

        requested_fields = [
            field.strip()
            for field in fields.split(",")
        ]

        allowed_fields = [
            "id",
            "customer_id",
            "status",
            "total"
        ]

        # -------------------------------------------------
        # Kiểm tra field không hợp lệ
        # -------------------------------------------------

        invalid_fields = [
            field
            for field in requested_fields
            if field not in allowed_fields
        ]

        if invalid_fields:

            raise ProblemError(
                title="Invalid fields",
                detail=(
                    "Unknown fields: "
                    + ", ".join(invalid_fields)
                ),
                status=400
            )

        # -------------------------------------------------
        # Chỉ trả về các field được yêu cầu
        # -------------------------------------------------

        page = [
            {
                field: order[field]
                for field in requested_fields
            }
            for order in page
        ]

    # =====================================================
    # 8. Response
    # =====================================================

    return jsonify({
        "data": page,
        "next_cursor": next_cursor,
        "has_more": has_more
    })


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":
     app.run(
            host="localhost",
            port=4040,
            debug=True
        )
