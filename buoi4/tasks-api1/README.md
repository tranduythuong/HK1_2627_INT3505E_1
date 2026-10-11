

```

- Swagger UI: http://127.0.0.1:5000/docs
- OpenAPI JSON: http://127.0.0.1:5000/openapi.json



## Luồng hoạt động theo 4 bước

1. **Marshmallow Schema → OpenAPI components:** `MarshmallowPlugin` chuyển `TaskSchema`, `CreateTaskSchema` và `UpdateTaskSchema` thành schema trong OpenAPI.
2. **YAML docstring → paths:** `FlaskPlugin` đọc YAML docstring trên từng view function để tạo các path và operation.
3. **`/openapi.json`:** `spec.to_dict()` xuất đặc tả OpenAPI thành Python dictionary rồi Flask trả JSON.
4. **`/docs`:** Swagger UI tải `/openapi.json`; người dùng có thể nhấn **Try it out** để gọi API thật.

## Năm endpoints

- `GET /v1/tasks`
- `POST /v1/tasks`
- `GET /v1/tasks/{task_id}`
- `PATCH /v1/tasks/{task_id}`
- `DELETE /v1/tasks/{task_id}`

Dữ liệu demo lưu trong bộ nhớ và sẽ reset khi server khởi động lại.

## Hai quyết định thiết kế

### 1. Dùng Marshmallow cho dữ liệu và OpenAPI schema

Schema được định nghĩa một lần và đăng ký vào `APISpec`; MarshmallowPlugin chuyển chúng thành reusable components. Các schema cũng được dùng để validate request đầu vào, giảm việc viết quy tắc dữ liệu lặp lại. Tuy vậy, response serialization vẫn cần được kiểm soát để tránh dữ liệu thực tế lệch khỏi schema.

### 2. Dùng YAML docstring để mô tả từng operation

Mô tả endpoint nằm cạnh hàm Flask tương ứng, giúp tìm code và tài liệu cùng một chỗ. Đổi lại, YAML trong docstring dễ sai indentation hoặc tham chiếu schema sai; cần kiểm tra `/openapi.json` và Swagger UI sau mỗi lần sửa.


