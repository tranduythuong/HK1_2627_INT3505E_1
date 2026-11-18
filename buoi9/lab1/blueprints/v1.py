"""Version 1 users API: user names are returned as ``full_name``."""

from flask import Blueprint, abort, jsonify


v1_blueprint = Blueprint("users_v1", __name__)

_USERS = {
    42: {"id": 42, "full_name": "Alex Nguyen"},
}


@v1_blueprint.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = _USERS.get(user_id)
    if user is None:
        abort(404, description="User not found")
    return jsonify(user)
