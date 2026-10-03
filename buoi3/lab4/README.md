### ĐÁNH GIÁ API DISCORD
6. Pagination

6.1 Collection có Pagination
Messages: GET /channels/{channel.id}/messages — Có pagination thông qua các tham số limit, before, after, around.
Guild Members: GET /guilds/{guild.id}/members — Có pagination thông qua các tham số limit, after.

6.2 Collection không có Pagination

Guild Channels: GET /guilds/{guild.id}/channels — Không có tham số pagination 

Guild Roles: GET /guilds/{guild.id}/roles — Không có tham số pagination 

Guild Invites: GET /guilds/{guild.id}/invites — Không có tham số pagination 

Kết luận: Discord API hỗ trợ pagination ở một số collection như Messages và Guild Members, nhưng không áp dụng cơ chế pagination cho tất cả collection.

07. Filter/Sort đa dạng

7.1 Collection có Filter/Sort
Messages Search: GET /guilds/{guild.id}/messages/search — Hỗ trợ lọc theo nội dung, người gửi (author_id), kênh (channel_id), trạng thái ghim (pinned) và các điều kiện khác. Hỗ trợ sắp xếp theo thời gian (timestamp) hoặc mức độ liên quan (relevance) thông qua sort_by, kết hợp với sort_order khi phù hợp.

7.2 Collection không có Filter/Sort đa dạng được công bố
Guild Channels: GET /guilds/{guild.id}/channels — Trả về danh sách kênh của server, không công bố các tham số lọc và sắp xếp tùy chỉnh như filter, sort_by.
Guild Roles: GET /guilds/{guild.id}/roles — Trả về danh sách role của server, không công bố cơ chế lọc và sắp xếp tùy chỉnh.

Sparse Fieldsets: Chưa có bằng chứng cho thấy Discord cung cấp cơ chế chung đểclient tùy chọn các trường dữ liệu trả về bằng tham số fields.

Kết luận: Discord hỗ trợ Filter/Sort đa dạng tại một số endpoint, tiêu biểu là tìm kiếm tin nhắn. Tuy nhiên, các khả năng này không được áp dụng thống nhất cho tất cả collection; đồng thời, chưa có đủ bằng chứng để khẳng định Discord hỗ trợ sparse fieldsets trên toàn bộ API.

