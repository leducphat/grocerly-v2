# SDD — Grocerly

*Đặc tả thiết kế phần mềm (Software Design Document)*

**Đề tài:** Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng
**Sinh viên:** Lê Đức Phát — 21139083 · **GVHD:** Hoàng Văn Dũng
**Đơn vị:** Trường ĐH Công nghệ Kỹ thuật TP.HCM — Khoa CNTT — Bộ môn Công nghệ Phần mềm

| | |
|---|---|
| Trạng thái | **Tài liệu sống** — mở cho chỉnh sửa |
| Nguồn gốc | Tách từ [`SRS.md`](SRS.md) Mục 7–9 ngày 11/09/2026 (P-07, D-011); nội dung gốc chuyển thể từ báo cáo TLCN `CLC_CNPM_1_LEDUCPHAT.pdf` |
| Cập nhật | 04/11/2026 |

> **Phạm vi của tài liệu này.** SDD trả lời câu hỏi *hệ thống được xây như thế
> nào*: mô hình dữ liệu, giao diện, công nghệ và thiết kế các thành phần. Còn *hệ
> thống phải làm gì* (tác nhân, yêu cầu chức năng/phi chức năng, use case) nằm ở
> [`SRS.md`](SRS.md).
>
> Cũng như SRS, file này phải **đúng như hiện trạng mã nguồn**, không phải như báo
> cáo cũ đã viết. Phát hiện chỗ nào lệch thì sửa thẳng file này và ghi lại lần sửa
> trong [`PLAN.md`](PLAN.md) §6 kèm lý do.
>
> File này chỉ có phần chữ. Sơ đồ thiết kế (lớp, tuần tự, trạng thái đơn, triển
> khai) vẽ trong báo cáo KLTN; bản nháp Mermaid để ở `docs/diagrams/`, không đưa
> vào Git (D-046).

---

## 1. Mô hình dữ liệu

14 bảng ở mức vật lý. Tên bảng theo Django app label.

| # | Bảng | Vai trò |
|---|---|---|
| 1 | `core_category` | Danh mục ngành hàng — có soft delete |
| 2 | `core_tag` | Thẻ phân loại (django-taggit) |
| 3 | `core_vendor` | Gian hàng / nhà cung cấp — có soft delete |
| 4 | `core_product` | Sản phẩm — có soft delete, trạng thái duyệt, tồn kho, HSD |
| 5 | `core_productimage` | Ảnh phụ của sản phẩm |
| 6 | `core_cartorder` | Đơn hàng: thông tin nhận hàng, thanh toán, vận chuyển |
| 7 | `core_cartorderitem` | Dòng chi tiết của đơn hàng: khóa ngoại `product` tới sản phẩm (`SET_NULL`), cột `item` giữ tên lúc mua (D-045) |
| 8 | `core_productreview` | Đánh giá + rating 1–5 |
| 9 | `core_wishlist` | Danh sách yêu thích |
| 10 | `core_address` | Địa chỉ giao hàng của người dùng |
| 11 | `core_coupon` | Mã giảm giá — có soft delete |
| 12 | `userauths_user` | Người dùng tùy biến — đăng nhập bằng email |
| 13 | `userauths_profile` | Hồ sơ mở rộng 1–1 với user |
| 14 | `userauths_contactus` | Tin nhắn liên hệ gửi ban quản trị |

### 1.1 Quy ước dữ liệu

- **Định danh công khai:** `Category.c_id`, `Vendor.v_id`, `Product.p_id`,
  `CartOrder.oid` là ShortUUID, dùng trong URL thay cho khóa chính số.
  `Product.sku` cũng là ShortUUID nhưng chỉ in ra làm mã sản phẩm trên trang chi
  tiết, không URL nào dùng. Chi tiết đơn của khách chuyển sang `oid` ngày
  04/11/2026 (L-32, D-047). Còn hai URL dùng khóa chính số: chi tiết đơn ở trang
  nhân viên, và `ajax-add-review/<int:p_id>/` (tên tham số là `p_id` nhưng nhận
  khóa chính).
- **Tiền tệ:** `DecimalField(max_digits=20, decimal_places=2)`, đơn vị VND.
- **Xóa mềm:** `core_category`, `core_vendor`, `core_product`, `core_coupon` mang
  cặp cờ `is_deleted` / `deleted_at`. `delete()` của bốn model này chỉ bật cờ, ở cả
  một dòng lẫn QuerySet; xóa hẳn phải gọi `hard_delete()` và không màn hình nào gọi
  nó (D-041). Khóa ngoại vẫn đọc được dòng đã xóa, nên chỗ nào đi từ khóa ngoại tới
  sản phẩm phải tự lọc: wishlist đi qua `wishlist_of()`. Xóa nhà cung cấp thì sản
  phẩm của họ bị xóa mềm theo, kể cả hai lệnh xóa hàng loạt trong Django admin:
  `SoftDeleteAdminMixin` gọi `soft_delete()` từng dòng thay cho một câu `UPDATE`
  (L-36).
- **Trạng thái sản phẩm:** `draft | disabled | in_review | rejected | published`.

### 1.2 Trạng thái đơn hàng

`CartOrder.product_status` nhận bốn giá trị của `STATUS_CHOICES`, mặc định
`processing` lúc `save_checkout_info` tạo đơn. Mọi bước chuyển đi qua
`change_order_status` của trang nhân viên, tra bảng `NEXT_STATUS` (D-032, D-033):
đơn chỉ đi tới từng bước, hoặc bị hủy khi chưa giao xong. Tồn kho bị trừ đúng một
lần, lúc đơn vào `shipped`. `paid_status` là một cột riêng chứ không phải trạng
thái: đơn COD thành đã thanh toán khi giao xong, đơn online chỉ thành đã thanh toán
ở `vnpay_return` hay `vnpay_ipn`. Riêng Django admin sửa thẳng được cột trạng thái,
bỏ qua `NEXT_STATUS`.

---

## 2. Danh sách giao diện

27 màn hình đã thiết kế và cài đặt.

**Xác thực (1–3):** Đăng nhập · Đăng ký · Quên/Đặt lại mật khẩu
**Mua sắm (4–13):** Trang chủ · Cửa hàng · Chi tiết sản phẩm · Đánh giá sản phẩm ·
Giỏ hàng · Thanh toán–Thông tin giao hàng · Thanh toán–Cổng thanh toán · Thanh
toán thành công · Yêu thích · Liên hệ
**Tài khoản (14–17):** Quản lý tài khoản · Lịch sử đơn hàng · Danh sách nhà cung
cấp · Chi tiết nhà cung cấp
**Quản trị (18–23):** Đăng nhập QTV · Dashboard Admin · Quản lý Danh mục · Quản lý
Người dùng · Quản lý Nhà cung cấp · Quản lý Mã giảm giá
**Nhân viên cửa hàng (24–27):** Dashboard nhân viên · Sản phẩm của Cửa hàng · Thêm/Sửa Sản
phẩm · Quản lý Đơn hàng

---

## 3. Công nghệ và dịch vụ tích hợp

| Tầng | Công nghệ |
|---|---|
| Front-end | HTML5, CSS3, JavaScript (AJAX), Bootstrap, jQuery |
| Back-end | Python, Django (kiến trúc MVT), Django REST Framework |
| CSDL | PostgreSQL, truy cập qua Django ORM |
| Giao diện quản trị | django-jazzmin |
| Trí tuệ nhân tạo | Google Gemini API (function calling) |
| Thanh toán | VNPay (Sandbox) + COD |
| Triển khai | Render (web service chạy `gunicorn`), tự build bằng `build.sh` (D-034); luồng deploy ở §3.2 |
| CI/CD | GitHub Actions, năm chặng: build (cài thư viện, `manage.py check`, kiểm migration), lint và phân tích tĩnh, test kèm độ phủ, quét secret, deploy. Chặng deploy chỉ chạy khi `main` có commit mới: gọi deploy hook của Render rồi chờ tới khi `/api/v1/health/` trả đúng commit vừa test (D-019, D-034, D-036) |
| Log ứng dụng | Logger `django` in ra stderr cả khi `DEBUG` tắt: lỗi 500 kèm traceback, 404 và 403 một dòng; logger `core` in cảnh báo của cửa hàng, hiện có một loại là số tiền VNPay báo khác giá đơn (L-34); xem và tìm ở trang Logs của Render (D-038) |
| CSDL đám mây | Neon (Serverless Postgres) |
| Lưu trữ media | Cloudinary (CDN) |

### 3.1 Thiết kế Trợ lý AI

Trợ lý được cấp **4 công cụ (function calling)**:

| Công cụ | Nhiệm vụ |
|---|---|
| `search_products(query)` | Tìm sản phẩm còn hàng khớp từ khóa, trả tối đa 5 kết quả |
| `get_bestsellers()` | Trả sản phẩm nổi bật khi khách hỏi "nên mua gì" |
| `request_add_to_cart(product_url_id, qty)` | Kích hoạt luồng thêm vào giỏ |
| `request_checkout()` | Kích hoạt luồng dẫn tới trang thanh toán |

Hai công cụ ghi (`request_add_to_cart`, `request_checkout`) **không tự thực thi**:
chúng trả về một `action` để giao diện hiển thị bước xác nhận cho người dùng. Đây
là ràng buộc thiết kế có chủ đích — AI không được tự ý thay đổi giỏ hàng của khách.
Một tin nhắn đi qua các công cụ này thế nào mô tả ở §4.2.

### 3.2 Triển khai

Mã nguồn đi từ máy sinh viên lên `develop`, vào `main` qua PR (D-016). Mỗi lần
push hay mở PR, GitHub Actions chạy bốn job kiểm tra; job `deploy` chỉ chạy khi
`main` có commit mới và bốn job kia xanh. Deploy hook chỉ mang mã commit: Render
tự lấy commit đó từ GitHub, chạy `build.sh` rồi mới chuyển sang server mới, nên job
`deploy` hỏi `/api/v1/health/` mỗi 20 giây, tối đa 15 phút, tới khi thấy đúng commit
(D-036). Khách đi qua VNPay bằng trình duyệt rồi quay về `vnpay_return`, còn IPN thì
VNPay gọi thẳng server.

> **Nợ thiết kế:** danh sách giao diện ở §2 và bảng công cụ ở §3.1 vẫn là bảng
> tóm tắt kế thừa từ TLCN, chưa kiểm lại từng dòng với mã nguồn. Xem
> [`PLAN.md`](PLAN.md) P-24.

---

## 4. Luồng xử lý chính

Hai luồng mà khách dùng nhiều nhất và có nhiều ràng buộc nhất.

### 4.1 Đặt hàng và thanh toán VNPay

`save_checkout_info` tính lại giá từ database bằng `_refresh_cart` (D-022), rồi ghi
đè đơn đang chờ trong session hoặc tạo đơn mới. VNPay báo kết quả qua hai kênh độc
lập: `vnpay_return` đi qua trình duyệt của khách, `vnpay_ipn` do VNPay gọi thẳng
server, và không kênh nào chắc tới trước. Cả hai chỉ đặt `paid_status` khi chữ ký
đúng, mã là `00` và số tiền khớp giá đơn lúc đó, qua cùng một hàm `_vnpay_amount`
(D-040), vì giá đơn đổi được sau khi khách đã mở link thanh toán. Mã IPN trả về
theo đúng thứ tự kiểm trong code: `99`, `97`, `01`, `04`, `02`, `00`.

### 4.2 Trợ lý AI thêm sản phẩm vào giỏ

Mỗi tin nhắn là một request `POST /api/v1/chat/` mang theo lịch sử lưu ở
`sessionStorage`; server không lưu hội thoại. `ai_chat` cho Gemini gọi tối đa ba
công cụ nối nhau trong một tin nhắn (L-30). Tìm kiếm chạy ngay trên server, còn
`request_add_to_cart` chỉ kiểm sản phẩm, tồn kho và số đã có trong giỏ rồi trả
`action: confirm_add_cart`, giỏ chưa đổi gì. Giỏ chỉ đổi khi khách bấm nút xác
nhận: khung chat gọi `/add-to-cart/` giống nút Add ở trang sản phẩm, nên giá và tồn
kho vẫn đi qua `_refresh_cart`, và câu báo sau đó đọc số lượng giỏ thật sự giữ
(D-044).

---

## 5. Lịch sử chỉnh sửa

Nhật ký các lần sửa file này được ghi chung với `SRS.md` tại [`PLAN.md`](PLAN.md)
§6. Khi sửa bất kỳ mục nào ở trên, thêm một dòng vào bảng đó: sửa gì, vì sao, và
commit tương ứng.
