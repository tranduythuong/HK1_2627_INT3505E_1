# Tasks API

REST API quản lý công việc, xây dựng bằng Flask và được mô tả bằng OpenAPI 3.0.3.

## 1. Chức năng (5 endpoints)

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/v1/tasks` | Liệt kê task; hỗ trợ `status` và `limit` |
| POST | `/v1/tasks` | Tạo task mới |
| GET | `/v1/tasks/{task_id}` | Lấy chi tiết task |
| PATCH | `/v1/tasks/{task_id}` | Cập nhật một phần task |
| DELETE | `/v1/tasks/{task_id}` | Xóa task |

## 2. Cài đặt và chạy

Yêu cầu Python 3.10 trở lên.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Nếu PowerShell chặn kích hoạt môi trường ảo, có thể gọi trực tiếp:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Mở các địa chỉ sau khi server chạy:

- Swagger UI: http://127.0.0.1:5000/docs
- OpenAPI JSON: http://127.0.0.1:5000/openapi.json
- API root: http://127.0.0.1:5000/

Swagger UI tải thư viện giao diện từ CDN nên cần kết nối Internet khi mở `/docs`.

## 3. Thử API bằng Swagger UI

1. Chạy Flask app.
2. Mở `http://127.0.0.1:5000/docs`.
3. Mở endpoint `GET /tasks`, nhấn **Try it out**, nhập `status=open`, `limit=10`, rồi nhấn **Execute**.
4. Mở `POST /tasks`, nhấn **Try it out**, nhập JSON:
   ```json
   {
     "title": "Test from Swagger UI",
     "description": "Create a task using Try it out",
     "status": "open"
   }
   ```
   Nhấn **Execute**. Kết quả dự kiến là `201`, cùng header `Location`.
5. Dùng ID trả về để thử `GET`, `PATCH` hoặc `DELETE /tasks/{task_id}`.
6. Chụp ảnh màn hình trang Swagger UI có endpoint mở rộng, phần **Try it out** và response sau khi nhấn **Execute**; lưu thành `screenshots/swagger-ui.png`.

> Lưu ý: `screenshots/swagger-ui.png` là nơi lưu ảnh chụp của bạn. Ảnh cần được chụp sau khi chạy ứng dụng thật; không nên dùng ảnh minh họa giả làm bằng chứng thử API.

## 4. Hai quyết định thiết kế khó nhất

### Quyết định 1: Dùng `PATCH` thay vì `PUT` cho cập nhật

Endpoint cập nhật là `PATCH /v1/tasks/{task_id}` vì client có thể chỉ gửi trường muốn thay đổi, chẳng hạn:

```json
{
  "status": "done"
}
```

Nếu dùng `PUT`, thông thường request đại diện cho việc thay thế toàn bộ tài nguyên, nên client cần gửi đầy đủ biểu diễn task. `PATCH` phù hợp hơn với yêu cầu cập nhật một phần. Đổi lại, server phải kiểm tra từng trường được gửi và từ chối trường không được hỗ trợ.

### Quyết định 2: Dùng mã trạng thái HTTP riêng cho từng tình huống

- `201 Created`: tạo task thành công; trả task mới và header `Location`.
- `200 OK`: đọc hoặc cập nhật task thành công.
- `204 No Content`: xóa thành công và không trả body.
- `400 Bad Request`: JSON hoặc query parameter không hợp lệ về cú pháp/kiểu.
- `404 Not Found`: ID task không tồn tại.
- `422 Unprocessable Entity`: JSON đọc được nhưng dữ liệu không đạt quy tắc nghiệp vụ, ví dụ thiếu `title` hoặc `status` không hợp lệ.

Việc phân biệt các mã này giúp client xử lý lỗi nhất quán thay vì trả `200` cho mọi tình huống. Trong một API lớn hơn, nhóm có thể chuẩn hóa cấu trúc lỗi và dùng chung qua `components/responses`.

## 5. Giới hạn của bản demo

- Dữ liệu đang lưu trong bộ nhớ; khởi động lại server sẽ khôi phục dữ liệu mẫu.
- Chưa có database, đăng nhập hoặc phân quyền.
- Swagger UI dùng CDN, vì vậy cần Internet để tải CSS/JavaScript.
- OpenAPI mô tả hợp đồng API; Flask vẫn phải tự thực hiện xác thực dữ liệu tương ứng.
