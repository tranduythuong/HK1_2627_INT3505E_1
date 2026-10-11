from flask import Flask, jsonify, request, Response, url_for
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields, validate

app = Flask(__name__)

# -------------------------------------------------------------------
# 1. Marshmallow schemas -> OpenAPI components
# -------------------------------------------------------------------

VALID_STATUSES = ("open", "in_progress", "done")


class TaskSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1))
    description = fields.String(load_default="")
    status = fields.String(
        load_default="open",
        validate=validate.OneOf(VALID_STATUSES),
    )
    created_by = fields.String(load_default="demo")


class CreateTaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1))
    description = fields.String(load_default="")
    status = fields.String(
        load_default="open",
        validate=validate.OneOf(VALID_STATUSES),
    )
    created_by = fields.String(load_default="demo")


class UpdateTaskSchema(Schema):
    title = fields.String(validate=validate.Length(min=1))
    description = fields.String()
    status = fields.String(validate=validate.OneOf(VALID_STATUSES))


# -------------------------------------------------------------------
# Demo data: in-memory storage, reset when the server restarts.
# -------------------------------------------------------------------

TASKS = [
    {
        "id": 1,
        "title": "Read REST constraints",
        "description": "Review the REST API notes",
        "status": "open",
        "created_by": "demo",
    },
    {
        "id": 2,
        "title": "Write OpenAPI spec",
        "description": "Document the five task endpoints",
        "status": "in_progress",
        "created_by": "demo",
    },
]
NEXT_ID = 3


def find_task(task_id):
    return next((task for task in TASKS if task["id"] == task_id), None)


def error(message, status):
    return jsonify({"error": {"status": status, "message": message}}), status


# -------------------------------------------------------------------
# 2. YAML docstrings -> OpenAPI paths
# Every docstring begins with --- followed by OpenAPI YAML.
# -------------------------------------------------------------------

@app.get("/v1/tasks")
def list_tasks():
    """List tasks, optionally filtered by status.
    ---
    get:
      tags: [tasks]
      summary: Lấy danh sách công việc
      operationId: listTasks
      parameters:
        - name: status
          in: query
          required: false
          schema:
            type: string
            enum: [open, in_progress, done]
          example: open
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 100
          example: 10
      responses:
        200:
          description: Danh sách task được lấy thành công
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Task'
        400:
          description: Query parameter không hợp lệ
    """
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
    """Create a task.
    ---
    post:
      tags: [tasks]
      summary: Tạo mới một task
      operationId: createTask
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTask'
      responses:
        201:
          description: Tạo task thành công
          headers:
            Location:
              description: URL của task vừa tạo
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        400:
          description: Request body không phải JSON hợp lệ
        422:
          description: Dữ liệu đầu vào không hợp lệ
    """
    global NEXT_ID

    if not request.is_json:
        return error("Content-Type must be application/json.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be a JSON object.", 400)

    errors = CreateTaskSchema().validate(data)
    if errors:
        return jsonify({"error": {"status": 422, "message": "Validation failed", "details": errors}}), 422

    clean_data = CreateTaskSchema().load(data)
    clean_data["title"] = clean_data["title"].strip()
    if not clean_data["title"]:
        return error("title must not be empty.", 422)

    task = {"id": NEXT_ID, **clean_data}
    NEXT_ID += 1
    TASKS.append(task)

    response = jsonify(task)
    response.status_code = 201
    response.headers["Location"] = url_for("get_task", task_id=task["id"])
    return response


@app.get("/v1/tasks/<int:task_id>")
def get_task(task_id):
    """Get one task by ID.
    ---
    get:
      tags: [tasks]
      summary: Lấy thông tin chi tiết một task
      operationId: getTask
      parameters:
        - in: path
          name: task_id
          required: true
          schema:
            type: integer
            minimum: 1
      responses:
        200:
          description: Lấy task thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        404:
          description: Không tìm thấy task
    """
    task = find_task(task_id)
    if task is None:
        return error("Task not found.", 404)
    return jsonify(task), 200


@app.patch("/v1/tasks/<int:task_id>")
def update_task(task_id):
    """Update selected fields of a task.
    ---
    patch:
      tags: [tasks]
      summary: Cập nhật một phần thông tin task
      operationId: updateTask
      parameters:
        - in: path
          name: task_id
          required: true
          schema:
            type: integer
            minimum: 1
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateTask'
      responses:
        200:
          description: Cập nhật task thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        400:
          description: Request body không hợp lệ
        404:
          description: Không tìm thấy task
        422:
          description: Dữ liệu đầu vào không hợp lệ
    """
    task = find_task(task_id)
    if task is None:
        return error("Task not found.", 404)
    if not request.is_json:
        return error("Content-Type must be application/json.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return error("Request body must be a non-empty JSON object.", 400)

    errors = UpdateTaskSchema().validate(data)
    if errors:
        return jsonify({"error": {"status": 422, "message": "Validation failed", "details": errors}}), 422

    allowed = {"title", "description", "status"}
    unknown = set(data) - allowed
    if unknown:
        return error(f"Unsupported fields: {', '.join(sorted(unknown))}.", 422)

    clean_data = UpdateTaskSchema().load(data)
    if "title" in clean_data:
        clean_data["title"] = clean_data["title"].strip()
        if not clean_data["title"]:
            return error("title must not be empty.", 422)

    task.update(clean_data)
    return jsonify(task), 200


@app.delete("/v1/tasks/<int:task_id>")
def delete_task(task_id):
    """Delete a task.
    ---
    delete:
      tags: [tasks]
      summary: Xóa một task
      operationId: deleteTask
      parameters:
        - in: path
          name: task_id
          required: true
          schema:
            type: integer
            minimum: 1
      responses:
        204:
          description: Xóa task thành công, không có response body
        404:
          description: Không tìm thấy task
    """
    task = find_task(task_id)
    if task is None:
        return error("Task not found.", 404)
    TASKS.remove(task)
    return "", 204


# -------------------------------------------------------------------
# 3. APISpec combines Marshmallow schemas + Flask YAML docstrings
# -------------------------------------------------------------------

spec = APISpec(
    title="Tasks API",
    version="1.0.0",
    openapi_version="3.0.3",
    info={
        "description": "API quản lý công việc (Tasks Management).",
    },
    servers=[{"url": "http://localhost:5000", "description": "Local development"}],
    tags=[{"name": "tasks", "description": "Quản lý công việc"}],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Register reusable Marshmallow schemas as OpenAPI components.
spec.components.schema("Task", schema=TaskSchema)
spec.components.schema("CreateTask", schema=CreateTaskSchema)
spec.components.schema("UpdateTask", schema=UpdateTaskSchema)

# FlaskPlugin reads each route path and parses its YAML docstring.
with app.test_request_context():
    spec.path(view=list_tasks)
    spec.path(view=create_task)
    spec.path(view=get_task)
    spec.path(view=update_task)
    spec.path(view=delete_task)


# -------------------------------------------------------------------
# 4. Serve the generated spec and Swagger UI
# -------------------------------------------------------------------

@app.get("/openapi.json")
def openapi_json():
    """Return the generated OpenAPI specification as JSON."""
    document = spec.to_dict()
    # Use the same host that the browser used to open the app.
    document["servers"] = [{
        "url": request.host_url.rstrip("/"),
        "description": "Current Flask server",
    }]
    return jsonify(document)


@app.get("/docs")
@app.get("/docs/")
def swagger_docs():
    """Render Swagger UI and load the generated spec from /openapi.json."""
    spec_url = url_for("openapi_json")
    html = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tasks API - Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  <style>
    html {{ box-sizing: border-box; }}
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
          "<h2>Không tải được Swagger UI</h2><p>Kiểm tra kết nối Internet/CDN rồi tải lại trang.</p>";
        return;
      }}
      SwaggerUIBundle({{
        url: {spec_url!r},
        dom_id: "#swagger-ui",
        deepLinking: true,
        displayRequestDuration: true,
        tryItOutEnabled: true,
        supportedSubmitMethods: ["get", "post", "patch", "delete"],
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
        validatorUrl: null
      }});
    }});
  </script>
</body>
</html>"""
    return Response(html, mimetype="text/html; charset=utf-8")


@app.get("/")
def index():
    return jsonify({
        "name": "Tasks API",
        "version": "1.0.0",
        "openapi": "/openapi.json",
        "docs": "/docs",
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
