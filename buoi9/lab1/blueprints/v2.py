"""Version 2 users API: user names are returned as first and last names."""

from flask import Blueprint, abort, jsonify


v2_blueprint = Blueprint("users_v2", __name__)

_USERS = {
    42: {"id": 42, "first_name": "Alex", "last_name": "Nguyen"},
}


@v2_blueprint.get("/users/<int:user_id>")
def get_user(user_id: int):
    user = _USERS.get(user_id)
    if user is None:
        abort(404, description="User not found")
    return jsonify(user)
