# Audit Public API: GitHub REST API

## 1. Tổng quan
API được audit là GitHub REST API public. Đây là API có thể truy cập công khai, dùng để đọc thông tin repo, user, issues, pull requests và nội dung file.

- Nhà cung cấp: GitHub
- Base URL: https://api.github.com
- Kiểu API: RESTful
- Đặc điểm: Dùng HTTP method chuẩn, URL biểu diễn tài nguyên, trả về JSON, có hỗ trợ pagination, filtering, và hypermedia links

## 2. Danh sách 5 endpoint

| STT | Endpoint | Method | Status code | Headers quan trọng | RESTful? |
|---|---|---|---:|---|---|
| 1 | https://api.github.com/repos/microsoft/vscode | GET | 200 OK | Content-Type, X-GitHub-Request-Id, X-RateLimit-Limit, X-RateLimit-Remaining, ETag | Có |
| 2 | https://api.github.com/users/octocat | GET | 200 OK | Content-Type, X-GitHub-Request-Id, X-RateLimit-Limit, X-RateLimit-Remaining, ETag | Có |
| 3 | https://api.github.com/repos/microsoft/vscode/issues | GET | 200 OK | Content-Type, Link, X-GitHub-Request-Id, X-RateLimit-Limit, ETag | Có |
| 4 | https://api.github.com/repos/microsoft/vscode/pulls | GET | 200 OK | Content-Type, Link, X-GitHub-Request-Id, X-RateLimit-Limit, ETag | Có |
| 5 | https://api.github.com/repos/microsoft/vscode/contents/README.md | GET | 200 OK | Content-Type, X-GitHub-Request-Id, X-RateLimit-Limit, ETag | Có |

## 3. Nhận xét chi tiết

### Endpoint 1: GET /repos/{owner}/{repo}
- Method: GET
- Mục đích: lấy thông tin chi tiết về repository
- Status: 200 OK
- Headers ghi nhận: Content-Type: application/json; charset=utf-8, Server: github.com, ETag
- Đánh giá: Đây là ví dụ chuẩn của REST: resource được đại diện qua URL và trả về JSON.

### Endpoint 2: GET /users/{username}
- Method: GET
- Mục đích: lấy thông tin tài khoản GitHub
- Status: 200 OK
- Headers: Content-Type, ETag, rate limit headers
- Đánh giá: URL biểu thị resource user rõ ràng, áp dụng nguyên tắc REST cơ bản.

### Endpoint 3: GET /repos/{owner}/{repo}/issues
- Method: GET
- Mục đích: liệt kê issue của repository
- Status: 200 OK
- Headers: Link cho pagination, cho thấy API hỗ trợ phân trang
- Đánh giá: Đây là resource collection, có phản ứng phù hợp với REST.

### Endpoint 4: GET /repos/{owner}/{repo}/pulls
- Method: GET
- Mục đích: lấy danh sách pull request
- Status: 200 OK
- Headers: Link chứa rel="next" và rel="last"
- Đánh giá: RESTful, vì pull request là một tập hợp resource có phân trang rõ ràng.

### Endpoint 5: GET /repos/{owner}/{repo}/contents/{path}
- Method: GET
- Mục đích: lấy nội dung file trong repo
- Status: 200 OK
- Headers: Content-Type và ETag
- Đánh giá: Resource file có URL rõ ràng, phù hợp với phong cách REST.

## 4. Kết luận
GitHub REST API là một API thực sự RESTful theo nhiều tiêu chí:
- URL biểu diễn tài nguyên rõ ràng
- Dùng phương thức HTTP chuẩn: GET, POST, PATCH, DELETE…
- Trả về JSON, có mã trạng thái HTTP rõ ràng
- Hỗ trợ pagination và caching headers
- Có các headers như Link, ETag, Cache-Control, rate-limit headers để phục vụ client tốt hơn

Tuy nhiên, GitHub API cũng có một số đặc điểm không hoàn toàn “thuần REST” kiểu nguyên mẫu học thuật vì có nhiều endpoint lồng ghép, filtering, và resource được phục vụ với các tính năng bổ sung như GraphQL, webhooks, và rate limiting. Nhưng về mặt thực tế, GitHub REST API vẫn là một ví dụ rất tốt của API public hiện đại và gần với RESTful.

## 5. Bản tóm tắt nhanh
- API chọn: GitHub REST API
- Số endpoint audit: 5
- Method sử dụng: GET
- Status code phổ biến: 200 OK
- Kết luận: Có tính RESTful rất cao, đúng chuẩn thực tế của API công khai hiện nay
