from flask import Flask, jsonify, request
from buoi3.lab2.ErrorHandler import ProblemError, register_error_handler
app = Flask(__name__)
register_error_handler(app)

POSTS = [
    {
        "id": 1,
        "title": "REST API là gì?",
        "content": "REST là một kiến trúc cho API.",
        "author_id": 1
    },
    {
        "id": 2,
        "title": "Học Flask",
        "content": "Flask là web framework của Python.",
        "author_id": 2
    }
]


@app.route("/test-error")
def test_error():
    raise RuntimeError("Database connection failed")

@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    return jsonify({
        "data": POSTS
    }), 200

@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    if not request.is_json:
        raise ProblemError(
            "Invalid request",
            "JSON is required",
            400
        )
    body = request.get_json(silent=True) or {}

    title = body.get("title")
    content = body.get("content")
    author_id = body.get("author_id")

    if not title:
        raise ProblemError("Invalid request", "title là bắt buộc", 400)

    if not content:
        raise ProblemError("Invalid request", "content là bắt buộc", 400)

    if not author_id:
        raise ProblemError("Invalid request", "author_id là bắt buộc", 400)

    new_post = {
        "id": len(POSTS) + 1,
        "title": title,
        "content": content,
        "author_id": author_id
    }

    POSTS.append(new_post)

    return jsonify({
        "data": new_post
    }), 201


@app.route('/api/v1/posts/<int:post_id>', methods = ["GET"])
def get_post(post_id):
    post = next(
    (post for post in POSTS if post['id'] == post_id),
    None
    )
    if post is None :
        raise ProblemError(
            title="Post does not exist",
            status=404,
            detail=f"Not post with id {post_id} does not exist"
        )
    return jsonify({
        "data": post
    }), 200



@app.route("/api/v1/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):

    post = next(
        (post for post in POSTS if post["id"] == post_id),
        None
    )

    if post is None:
        raise ProblemError("Post does not exist", f"Post with id {post_id} does not exist", 404)

    body = request.get_json(silent=True) or {}

    if not request.is_json:
        raise ProblemError("Invalid request", "JSON is required", 400)

    title = body.get("title")
    content = body.get("content")
    author_id = body.get("author_id")

    if not title or not content or not author_id:
        raise ProblemError("Invalid request", "title, content, author_id là bắt buộc", 400)

    post["title"] = title
    post["content"] = content
    post["author_id"] = author_id

    return jsonify({
        "data": post
    }), 200


@app.route("/api/v1/posts/<int:post_id>", methods=["PATCH"])
def patch_post(post_id):

    post = next(
        (post for post in POSTS if post["id"] == post_id),
        None
    )

    if post is None:
        raise ProblemError("Post does not exist", f"Post with id {post_id} does not exist", 404)

    body = request.get_json(silent=True) or {}

    if not request.is_json:
        raise ProblemError("Invalid request", "JSON is required", 400)

    if "title" in body:
        post["title"] = body["title"]

    if "content" in body:
        post["content"] = body["content"]

    if "author_id" in body:
        post["author_id"] = body["author_id"]

    return jsonify({
        "data": post
    }), 200


@app.route("/api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):

    post = next(
        (post for post in POSTS if post["id"] == post_id),
        None
    )

    if post is None:
        raise ProblemError("Post does not exist", f"Post with id {post_id} does not exist", 404)

    POSTS.remove(post)

    return "", 204


if __name__ == "__main__":
    app.run(
        host="localhost",
        port=4040,
        debug=True
    )
