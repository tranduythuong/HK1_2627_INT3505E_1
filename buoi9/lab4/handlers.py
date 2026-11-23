"""Order handlers for the blue-green routing exercise."""


def v1_create_order(body):
    return {
        "order_id": "v1-" + body["account_id"],
        "account_id": body["account_id"],
        "status": "created",
        "api_version": 1,
    }


def v2_create_order(body):
    return {
        "order_id": "v2-" + body["account_id"],
        "account_id": body["account_id"],
        "status": "accepted",
        "api_version": 2,
    }
