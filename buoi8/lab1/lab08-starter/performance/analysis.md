# Lab 4 — Phân tích kết quả

Đo ngày 17/11/2026 trên máy local bằng Locust 2.47.0, Flask development server
và SQLite; workload dùng `performance/locustfile.py`, gồm list, read, create
và tìm kiếm theo năm. Các kịch bản chạy tuần tự trên cùng database; dữ liệu do
các request POST tạo ra được giữ lại giữa các lần chạy.

| Kịch bản | Users | Spawn rate | Duration | Requests | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 143 | 18 | 0% | 4.88 |
| B | 50 | 5 | 60s | 1,379 | 22 | 0% | 23.23 |
| C | 200 | 50 | 30s | 2,825 | 100 | 0% | 96.24 |

1. **C có p95 cao nhất**: p95 tăng từ 18 ms (10 users) lên 22 ms (50 users)
   và 100 ms (200 users). RPS tăng cùng tải từ 4.88 lên 23.23 và 96.24.
   Ở C, p95 tổng là 100 ms nhưng request chậm nhất là 408 ms; riêng POST có
   p95 140 ms. Các giá trị p95 do Locust ước lượng.
2. **Không endpoint nào ghi nhận failure** trong ba lần chạy. (GET
   `/books/{id}` có thể nhận 404 với ID ngẫu nhiên; script coi 404 là kết quả
   dự kiến và gọi `response.success()`). Không có HTTP 500 và cũng không có
   lỗi giả lập bằng `response.failure()`; vì thế failure rate của Locust là 0%.
3. **A, B, C đều đạt** ngưỡng giả định p95 < 300 ms. Đây chỉ là phép đo local
   ngắn với Flask development server và SQLite, trên một máy; các lần chạy
   dùng chung database nên số bản ghi tăng dần. Không có nhiều lần lặp, giám
   sát tài nguyên, hay môi trường production tương đương. Kết quả không chứng
   minh SLO production.
4. Để kiểm tra pool tối đa 5 kết nối, trước hết xác nhận DB/pool đang dùng và
   cấu hình `pool_size=5`, `max_overflow=0` trên backend hỗ trợ các tùy chọn
   này. Sau đó chạy lại cùng workload với dữ liệu và máy được giữ cố định,
   đối chiếu p95/RPS/failure rate và thời gian chờ lấy kết nối. SQLite có khóa
   ghi riêng nên cần tách ảnh hưởng khóa DB khỏi giới hạn pool; có thể chạy
   thêm trên DB client/server như PostgreSQL để đo pool rõ ràng hơn.

HTML report được lưu tại `reports/A.html`, `reports/B.html`, `reports/C.html`.

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.
