### Security Audit — Social Network API

## Phạm vi
Tài liệu rà soát ba endpoint POST /auth/login, POST /auth/refresh và GET /posts/{id} dựa trên năm nguyên tắc Auth. Các mục dưới đây là rủi ro cần kiểm tra trong quá trình triển khai, không khẳng định hệ thống chắc chắn đang mắc lỗi.
1. AuthN ≠ AuthZ — Không tách xác thực và phân quyền
Nguy cơ có thể lộ: API chỉ kiểm tra người dùng đã đăng nhập mà không kiểm tra họ có quyền thực hiện hành động hoặc xem đúng bài viết hay không. Điều này có thể khiến người dùng đọc được bài viết riêng tư hoặc dữ liệu của tài khoản khác.

Áp dụng cho API:
- POST /auth/login: xác minh thông tin đăng nhập; không coi việc đăng nhập thành công là quyền truy cập mọi tài nguyên.
- POST /auth/refresh: xác minh refresh token, trạng thái phiên và quyền được làm mới.
- GET /posts/{id}: kiểm tra cả danh tính, scope posts:read và chính sách truy cập bài viết cụ thể.
Giảm thiểu: Kiểm thử riêng xác thực (AuthN) và phân quyền (AuthZ), kể cả trường hợp token hợp lệ nhưng không đủ quyền.
2. Chọn cơ chế theo context — Cookie-session, JWT và OAuth 2.0 khác lớp
Nguy cơ có thể lộ: Chọn cơ chế không phù hợp hoặc kết hợp sai có thể làm lộ phiên đăng nhập, token hoặc thông tin xác thực. JWT là định dạng token, cookie là cách vận chuyển/lưu trữ, còn OAuth 2.0 là framework ủy quyền; chúng không phải các lựa chọn thay thế trực tiếp cho nhau.

Áp dụng cho API: Xác định client là web, mobile hay service-to-service trước khi quyết định nơi lưu token và cách truyền credential. Không đưa token vào URL hoặc log.

Giảm thiểu: Chỉ dùng HTTPS; nếu dùng cookie thì cân nhắc HttpOnly, Secure, SameSite và bảo vệ CSRF phù hợp. Nếu dùng bearer token, tránh lưu trữ ở nơi dễ bị JavaScript đọc khi có XSS và không cache response nhạy cảm.
3. JWT cần discipline — Kiểm tra token chặt chẽ và quản lý vòng đời
Nguy cơ có thể lộ: Chấp nhận thuật toán không mong muốn, bỏ qua các claim cần thiết, dùng access token quá lâu hoặc không thu hồi refresh token có thể khiến token bị giả mạo hoặc bị đánh cắp tiếp tục sử dụng.

Áp dụng cho API:
- GET /posts/{id}: xác minh chữ ký, thuật toán trong allowlist, iss, aud, exp và các claim bắt buộc theo profile của hệ thống.
- POST /auth/refresh: kiểm tra hạn dùng, trạng thái thu hồi và việc refresh token đã được sử dụng hay chưa.
Giảm thiểu: Dùng thư viện được duy trì; đặt access token thời hạn ngắn; refresh token rotation và phát hiện reuse; lập kế hoạch xoay vòng/thu hồi khóa và thu hồi token. Không tự viết thuật toán JWT.
4. Phân quyền theo chính sách — Danh tính, hành động và đối tượng
Nguy cơ có thể lộ: Chỉ kiểm tra scope posts:read mà không xét quyền đối với bài viết cụ thể có thể gây lỗi IDOR/BOLA, làm lộ bài viết riêng tư, bài viết của tenant khác hoặc nội dung chỉ dành cho người theo dõi.

Áp dụng cho API: GET /posts/{id} cần áp dụng chính sách dựa trên danh tính người gọi, hành động read, đối tượng bài viết và ngữ cảnh như visibility, quan hệ theo dõi, vai trò hoặc tenant.

Giảm thiểu: Kiểm tra quyền trên server cho từng đối tượng; không tin id do client cung cấp là bằng chứng sở hữu. Với tài nguyên riêng tư, cân nhắc phản hồi 404 thay cho 403 nếu chính sách cần tránh tiết lộ tài nguyên có tồn tại hay không. Quy tắc ownership chỉ là một ví dụ; dữ liệu chia sẻ và multi-tenant cần chính sách riêng.
5. Hash mật khẩu đúng — Không lưu hoặc ghi lộ mật khẩu
Nguy cơ có thể lộ: Lưu mật khẩu dạng rõ, dùng hash nhanh/không phù hợp, thiếu salt, ghi password vào log hoặc trả thông tin lỗi quá cụ thể có thể làm tăng rủi ro chiếm đoạt tài khoản.

Áp dụng cho API: POST /auth/login nhận mật khẩu qua HTTPS, kiểm tra bằng hàm xác minh hash chuyên dụng và không bao giờ trả lại mật khẩu. Log, tracing và báo lỗi phải che dữ liệu nhạy cảm.

Giảm thiểu: Dùng Argon2id hoặc phương án phù hợp theo khuyến nghị hiện hành, với salt riêng và cost được cấu hình hợp lý; nâng tham số và rehash khi cần. Không áp dụng lịch đổi mật khẩu định kỳ thiếu căn cứ; yêu cầu đổi khi có dấu hiệu lộ lọt hoặc theo chính sách rủi ro phù hợp.