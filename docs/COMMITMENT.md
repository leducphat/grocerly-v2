# BẢN CAM KẾT SẢN PHẨM — Grocerly (KLTN)

> **⚠️ BẢN NHÁP — chưa ký.** Soạn ngày 10/09/2026 để trao đổi với GVHD. Phần
> chức năng (§2) đã đối chiếu với mã nguồn; phần metric và KPI (§5) chưa soạn.

| | |
|---|---|
| Đề tài | Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng |
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| Hạn chốt | **25/10/2026** — hết Tuần 7, mốc 50% thời gian (rubric Mục 2 Bước 3, gate G1) |
| Theo dõi | [`PLAN.md`](PLAN.md) P-03 |

**Vì sao văn bản này quan trọng.** Rubric TC2.2 chấm theo *"tỉ lệ chức năng đã cam
kết ở Bước 3 hoạt động"* — danh sách ở §2 chính là mẫu số. Cam kết quá nhiều thì
tự hạ điểm TC2.2; cam kết quá ít thì dính gate G9 (sản phẩm không tương xứng khối
lượng). Vì vậy danh sách dưới đây chỉ gồm **chức năng đã có trong mã nguồn**, cộng
các sửa lỗi nghiệp vụ — không có tính năng mới (D-008).

---

## 1. Sản phẩm cuối cùng

Website thương mại điện tử bán thực phẩm theo **mô hình một nhà bán** (D-015): một
cửa hàng duy nhất bán hàng của nhiều nhà cung cấp. "Nhà cung cấp" (model `Vendor`)
chỉ là thông tin nguồn hàng gắn với sản phẩm, không phải tài khoản người bán.
Sản phẩm gồm:

- **Cửa hàng trực tuyến** cho khách vãng lai và khách hàng: duyệt, tìm kiếm, giỏ
  hàng, đặt hàng, thanh toán VNPay (sandbox) hoặc COD, hai ngôn ngữ vi/en.
- **Trợ lý AI** (Google Gemini, function calling) tìm sản phẩm, đề xuất thêm vào
  giỏ và dẫn tới thanh toán qua hội thoại — thao tác ghi cần người dùng xác nhận.
- **Trang quản lý cho nhân viên** (`/useradmin/`): sản phẩm, tồn kho, đơn hàng,
  thống kê.
- **Trang quản trị cho quản trị viên** (Django admin): danh mục, người dùng, mã
  giảm giá, nhà cung cấp, toàn bộ sản phẩm và đơn hàng.

Sản phẩm được triển khai trên **hạ tầng riêng của KLTN** (D-002), truy cập công
khai qua Internet, kèm pipeline CI/CD.

---

## 2. Danh sách chức năng cam kết

Cột **Hiện trạng**:
- `Có` — route và view đã có trong mã nguồn.
- `Lệch` — có, nhưng hành vi khác đặc tả TLCN hoặc có lỗi; cách xử lý ở §3.

Hành vi chi tiết của từng chức năng sẽ được kiểm lại khi viết acceptance criteria
ở P-23.

### 2.1 Khách vãng lai và Khách hàng — cửa hàng trực tuyến

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-01 | Đăng ký tài khoản bằng email | UC-01 | Có |
| CN-02 | Đăng nhập, đăng xuất | UC-02, UC-10 | Có |
| CN-03 | Quên mật khẩu — đặt lại qua email | *(chưa có UC)* | Có |
| CN-04 | Xem trang chủ, danh sách sản phẩm, sản phẩm theo danh mục và theo thẻ | UC-03 | Có |
| CN-05 | Xem chi tiết sản phẩm: giá, mô tả, ảnh, đánh giá, sản phẩm liên quan | UC-04 | Có |
| CN-06 | Tìm sản phẩm theo tên; lọc theo danh mục, nhà cung cấp, khoảng giá | UC-05 | Có |
| CN-07 | Xem danh sách và trang chi tiết nhà cung cấp | *(chưa có UC)* | Có |
| CN-08 | Giỏ hàng: thêm, cập nhật số lượng, xóa; không cho vượt tồn kho | UC-06 | **Lệch** — L-7 |
| CN-09 | Đổi ngôn ngữ vi ↔ en | UC-07 | Có |
| CN-10 | Gửi liên hệ tới ban quản trị | UC-08 | Có |
| CN-11 | Thanh toán: nhập thông tin giao hàng, áp mã giảm giá, chọn COD hoặc VNPay | UC-09 | **Lệch** — L-6 |
| CN-12 | Cập nhật hồ sơ cá nhân, đổi mật khẩu | UC-11 | Có |
| CN-13 | Danh sách yêu thích: thêm, xem, xóa | UC-12 | Có |
| CN-14 | Xem lịch sử đơn mua và chi tiết từng đơn; đặt địa chỉ mặc định | UC-13 | Có |
| CN-15 | Đánh giá và chấm điểm sản phẩm (1–5 sao) | UC-14 | **Lệch** — L-3, L-4 |

### 2.2 Trợ lý AI

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-16 | Hỏi đáp, tư vấn bằng ngôn ngữ tự nhiên | UC-15 | Có |
| CN-17 | AI tìm sản phẩm còn hàng theo nhu cầu | UC-16 | Có |
| CN-18 | AI đề xuất thêm vào giỏ — chỉ thêm khi người dùng xác nhận | UC-17 | Có |
| CN-19 | AI dẫn người dùng tới trang thanh toán | UC-18 | Có |

*Công cụ `get_bestsellers` (gợi ý sản phẩm "nổi bật") vẫn còn trong mã nguồn nhưng
**không thuộc cam kết**: nó chỉ lấy sản phẩm gắn cờ `featured` thủ công, không tính
doanh số thật.*

### 2.3 Nhân viên cửa hàng — `/useradmin/`

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-20 | Dashboard: doanh thu, doanh thu theo tháng, số đơn, khách hàng mới | UC-26 | Có |
| CN-21 | Quản lý sản phẩm: thêm, sửa, xóa mềm, cập nhật tồn kho, quản lý ảnh | UC-19 | **Lệch** — L-1, L-2 |
| CN-22 | Quản lý đơn hàng: xem, đổi trạng thái giao hàng; không có thao tác xóa đơn | UC-20 | **Lệch** — L-5 |
| CN-23 | Xem danh sách đánh giá; cập nhật hồ sơ và đổi mật khẩu nhân viên | *(chưa có UC)* | Có |

### 2.4 Quản trị viên — Django admin

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-24 | Quản lý mã giảm giá: tạo, sửa, bật/tắt, xóa mềm và khôi phục | UC-21 | Có |
| CN-25 | Quản lý người dùng: tra cứu, phân quyền, khóa tài khoản | UC-22 | Có |
| CN-26 | Quản lý danh mục: thêm, sửa, xóa mềm và khôi phục | UC-23 | Có |
| CN-27 | Quản lý toàn bộ sản phẩm: đổi trạng thái hiển thị, xóa mềm và khôi phục | UC-24 | **Lệch** — L-2 |
| CN-28 | Tra cứu toàn bộ đơn hàng, lọc theo trạng thái thanh toán và giao hàng | UC-25 | Có |
| CN-29 | Quản lý nhà cung cấp: thêm, sửa, xóa mềm và khôi phục | *(chưa có UC)* | Có |
| CN-30 | Xem hộp thư liên hệ | *(chưa có UC)* | Có |

**Tổng: 30 chức năng** — 24 `Có`, 6 `Lệch`. Các chức năng CN-03, 07, 23, 29, 30 có
trong mã nguồn nhưng đặc tả TLCN chưa có use case; sẽ bổ sung UC ở P-23.

---

## 3. Những chỗ lệch giữa đặc tả TLCN và mã nguồn — cần chốt

Mỗi chỗ có hai cách: **sửa đặc tả** cho khớp code, hoặc **sửa code** cho khớp đặc
tả. Cột "Đề xuất" là ý kiến ban đầu, chờ sinh viên và GVHD quyết.

| Mã | Đặc tả TLCN nói | Mã nguồn thực tế | Đề xuất |
|---|---|---|---|
| **L-1** | Người bán quản lý **gian hàng riêng**, thống kê của riêng gian hàng (A3, FR-V-04) | Không có vai trò người bán riêng: ai có `is_staff` đều vào `/useradmin/` và thấy **toàn bộ** sản phẩm, đơn hàng, doanh thu (`useradmin/views.py`) | ✅ **Đã chốt — sửa đặc tả** (D-015): mô hình một nhà bán, A3 là *nhân viên cửa hàng*. `SRS.md` đã sửa ngày 11/09/2026 |
| **L-2** | Sản phẩm người bán tạo ở trạng thái `in_review`, Admin duyệt sang `published` mới hiển thị (UC-19, UC-24) | `add_product` gán thẳng `product_status = 'published'` — không có bước duyệt | **Sửa đặc tả** — đi cùng L-1: nhân viên của chính cửa hàng thì bước duyệt không có ý nghĩa nghiệp vụ. Admin vẫn ẩn/gỡ được sản phẩm |
| **L-3** | Chỉ đánh giá được sản phẩm **đã mua** (đơn `Shipped`) (UC-14) | Chỉ kiểm tra "chưa từng đánh giá sản phẩm này"; `ajax_add_review` không kiểm tra đăng nhập, không kiểm tra đã mua | **Sửa code:** quy tắc nghiệp vụ hợp lý và là lỗ hổng thật (ai cũng gửi được đánh giá). Kèm test ca âm |
| **L-4** | Đánh giá có đủ CRUD (UC-14) | Khách chỉ **tạo** được; sửa/xóa chỉ làm được trong Django admin | **Sửa đặc tả:** khách tạo đánh giá, quản trị viên kiểm duyệt |
| **L-5** | Đơn đã `Delivered` không được đổi trạng thái nữa (UC-20) | `change_order_status` không chặn — đổi được từ bất kỳ trạng thái nào | **Sửa code:** thêm điều kiện chặn, kèm test ca âm |
| **L-6** 🔴 | *(đặc tả không nói tới — mặc định giá lấy từ hệ thống)* | **Giá do trình duyệt gửi lên.** `add_to_cart` lưu `price` từ tham số GET vào session; `save_checkout_info` tính `order.price` từ giá đó; số tiền gửi sang VNPay là `order.price`. Khách sửa tham số là đặt được hàng với giá tùy ý. Tiền còn tính bằng `float` thay vì `Decimal` | **Sửa code — ưu tiên cao nhất.** Server tự tra giá từ `Product` khi thêm giỏ và khi tạo đơn; dùng `Decimal`. Viết test tái hiện lỗi trước (regression test) rồi mới sửa |
| **L-7** | Cập nhật số lượng lớn hơn tồn kho → báo lỗi, reset về số hợp lệ (UC-06) | `add_to_cart`, `update_cart` và `save_checkout_info` không kiểm tra tồn kho ở server | **Sửa code:** kiểm tra tồn kho ở server khi thêm giỏ và khi tạo đơn, kèm test ca biên |

Đã chốt: L-1. Nếu các chỗ còn lại chốt theo đề xuất: thêm **2 lần sửa đặc tả**
(L-2, L-4 — ghi vào `PLAN.md` §6) và **4 lần sửa code** (L-3, L-5, L-6, L-7), mỗi
lần có test đi kèm.

---

## 4. Ngoài cam kết

Không làm trong KLTN, đưa vào mục *"Các hướng phát triển mở rộng"* (D-008):

- Mô hình nhiều người bán (marketplace), gian hàng và thống kê riêng từng người bán
- Tìm kiếm full-text, gợi ý từ khóa
- Thống kê đa chiều nâng cao
- Live chat thời gian thực giữa khách và cửa hàng
- Gợi ý sản phẩm bằng Machine Learning
- Ứng dụng di động

---

## 5. Metric và KPI — *chưa soạn*

Sẽ bổ sung trước khi trình ký. Khung dự kiến:

- **KPI nghiệp vụ** (TC1 Mức 5 cần ≥ 5, định lượng): ví dụ tỉ lệ đặt hàng thành
  công qua trợ lý AI, số bước từ tìm sản phẩm tới đặt hàng, thời gian phản hồi
  của trợ lý…
- **Metric kỹ thuật** theo rubric Mục 5 — độ phủ test, số chặng CI/CD, số lần
  deploy, tỉ lệ build xanh, lỗi lint, secret lộ, người dùng thực nghiệm, SUS.
  Rubric cho phép điều chỉnh ngưỡng tại bước này.
- **Cách hiểu "Pull Request có review" cho đồ án một người** (D-012).
- **Cách lấy ý kiến bên liên quan** gộp vào thực nghiệm người dùng (D-013).

---

## 6. Xác nhận

| Sinh viên | Giảng viên hướng dẫn |
|---|---|
| | |
| Lê Đức Phát | Hoàng Văn Dũng |
| Ngày: | Ngày: |
