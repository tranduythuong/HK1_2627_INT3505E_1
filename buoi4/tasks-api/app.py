from copy import deepcopy
from pathlib import Path


from flask import Flask, jsonify, request, Response, url_for

app = Flask(__name__)
OPENAPI_PATH = Path(__file__).with_name("openapi.yaml")

# Demo data: in-memory storage, reset whenever the server restarts.
TASKS = [
    {"id": 1, "title": "Read REST constraints", "description": "Review the REST API notes",
     "status": "open", "created_by": "demo"},
    {"id": 2, "title": "Write OpenAPI spec", "description": "Document the five task endpoints",
     "status": "in_progress", "created_by": "demo"},
]
NEXT_ID = 3
VALID_STATUSES = {"open", "in_progress", "done"}


def find_task(task_id):
    return next((task for task in TASKS if task["id"] == task_id), None)


def error(message, status):
    return jsonify({"error": {"status": status, "message": message}}), status


@app.get("/")
def index():
    return jsonify({
        "name": "Tasks API",
        "version": "1.0.0",
        "openapi": "/openapi.json",
        "docs": "/docs"
    })


@app.get("/openapi.json")
def openapi_json():
    """Return the OpenAPI document parsed from openapi.yaml as JSON.

    The server URL is generated from the current request host. This avoids a
    localhost/127.0.0.1 mismatch when Swagger UI sends requests to the API.
    """
    try:
        spec = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
        if not isinstance(spec, dict) or not str(spec.get("openapi", "")).startswith("3."):
            return error("openapi.yaml must contain a valid OpenAPI 3.x document.", 500)

        # Keep openapi.yaml as the source of truth, but make its server host
        # match the host used to open Swagger UI in the browser.
        spec = deepcopy(spec)
        spec["servers"] = [{
            "url": f"{request.host_url.rstrip('/')}/v1",
            "description": "Current Flask server"
        }]
        return jsonify(spec)
    except (OSError, yaml.YAMLError):
        app.logger.exception("Could not load openapi.yaml")
        return error("OpenAPI specification could not be loaded.", 500)


@app.get("/docs")
@app.get("/docs/")
def swagger_docs():
    """Render Swagger UI and load the live specification from /openapi.json."""
    spec_url = url_for("openapi_json")
    html = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tasks API - Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  <style>
    html {{ box-sizing: border-box; overflow-y: scroll; }}
    *, *::before, *::after {{ box-sizing: inherit; }}
    body {{ margin: 0; background: #fafafa; }}
    #swagger-ui {{ max-width: 1400px; margin: 0 auto; }}
    .topbar {{ display: none; }}
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.addEventListener("load", function () {{
      if (typeof SwaggerUIBundle === "undefined") {{
        document.getElementById("swagger-ui").innerHTML =
          "<h2>Không tải được Swagger UI</h2><p>Hãy kiểm tra kết nối Internet/CDN rồi tải lại trang.</p>";
        return;
      }}
      SwaggerUIBundle({{
        url: {spec_url!r},
        dom_id: "#swagger-ui",
        deepLinking: true,
        displayRequestDuration: true,
        filter: true,
        tryItOutEnabled: true,
        supportedSubmitMethods: ["get", "post", "put", "patch", "delete", "options", "head"],
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
        validatorUrl: null
      }});
    }});
  </script>
</body>
</html>"""
    return Response(html, mimetype="text/html; charset=utf-8")


@app.get("/v1/tasks")
def list_tasks():
    status = request.args.get("status")
    if status and status not in VALID_STATUSES:
        return error("status must be open, in_progress, or done.", 400)

    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return error("limit must be an integer.", 400)
    if limit < 1 or limit > 100:
        return error("limit must be between 1 and 100.", 400)

    result = TASKS
    if status:
        result = [task for task in result if task["status"] == status]
    return jsonify(result[:limit]), 200


@app.post("/v1/tasks")
def create_task():
    global NEXT_ID
    if not request.is_json:
        return error("Content-Type must be application/json.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be a JSON object.", 400)

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return error("title is required and must be a non-empty string.", 422)

    status = data.get("status", "open")
    if status not in VALID_STATUSES:
        return error("status must be open, in_progress, or done.", 422)

    description = data.get("description", "")
    if not isinstance(description, str):
        return error("description must be a string.", 422)

    task = {
        "id": NEXT_ID,
        "title": title.strip(),
        "description": description,
        "status": status,
        "created_by": data.get("created_by", "demo"),
    }
    NEXT_ID += 1
    TASKS.append(task)
    response = jsonify(task)
    response.status_code = 201
    response.headers["Location"] = f"/v1/tasks/{task['id']}"
    return response


@app.get("/v1/tasks/<int:task_id>")
def get_task(task_id):
    task = find_task(task_id)
    if task is None:
        return error("Task not found.", 404)
    return jsonify(task), 200


@app.patch("/v1/tasks/<int:task_id>")
def update_task(task_id):
    task = find_task(task_id)
    if task is None:
        return error("Task not found.", 404)
    if not request.is_json:
        return error("Content-Type must be application/json.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error("Request body must be a non-empty JSON object.", 400)

    allowed = {"title", "description", "status"}
    unknown = set(data) - allowed
    if unknown:
        return error(f"Unsupported fields: {', '.join(sorted(unknown))}.", 422)

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return error("title must be a non-empty string.", 422)
        task["title"] = data["title"].strip()

    if "description" in data:
        if not isinstance(data["description"], str):
            return error("description must be a string.", 422)
        task["description"] = data["description"]

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return error("status must be open, in_progress, or done.", 422)
        task["status"] = data["status"]

    return jsonify(task), 200


@app.delete("/v1/tasks/<int:task_id>")
def delete_task(task_id):
    task = find_task(task_id)
    if task is None:
        return error("Task not found.", 404)
    TASKS.remove(task)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
