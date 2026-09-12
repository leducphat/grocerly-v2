# SDD — Grocerly

*Đặc tả thiết kế phần mềm (Software Design Document)*

**Đề tài:** Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng
**Sinh viên:** Lê Đức Phát — 21139083 · **GVHD:** Hoàng Văn Dũng
**Đơn vị:** Trường ĐH Công nghệ Kỹ thuật TP.HCM — Khoa CNTT — Bộ môn Công nghệ Phần mềm

| | |
|---|---|
| Trạng thái | **Tài liệu sống** — mở cho chỉnh sửa |
| Nguồn gốc | Tách từ [`SRS.md`](SRS.md) Mục 7–9 ngày 11/09/2026 (P-07, D-011); nội dung gốc chuyển thể từ báo cáo TLCN `CLC_CNPM_1_LEDUCPHAT.pdf` |
| Cập nhật | 11/09/2026 |

> **Phạm vi của tài liệu này.** SDD trả lời câu hỏi *hệ thống được xây như thế
> nào*: mô hình dữ liệu, giao diện, công nghệ và thiết kế các thành phần. Còn *hệ
> thống phải làm gì* (tác nhân, yêu cầu chức năng/phi chức năng, use case) nằm ở
> [`SRS.md`](SRS.md).
>
> Cũng như SRS, file này phải **đúng như hiện trạng mã nguồn**, không phải như báo
> cáo cũ đã viết. Phát hiện chỗ nào lệch thì sửa thẳng file này và ghi lại lần sửa
> trong [`PLAN.md`](PLAN.md) §6 kèm lý do.

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
| 7 | `core_cartorderitem` | Dòng chi tiết của đơn hàng |
| 8 | `core_productreview` | Đánh giá + rating 1–5 |
| 9 | `core_wishlist` | Danh sách yêu thích |
| 10 | `core_address` | Địa chỉ giao hàng của người dùng |
| 11 | `core_coupon` | Mã giảm giá — có soft delete |
| 12 | `userauths_user` | Người dùng tùy biến — đăng nhập bằng email |
| 13 | `userauths_profile` | Hồ sơ mở rộng 1–1 với user |
| 14 | `userauths_contactus` | Tin nhắn liên hệ gửi ban quản trị |

### 1.1 Quy ước dữ liệu

- **Định danh công khai:** `Category.c_id`, `Vendor.v_id`, `Product.p_id`,
  `Product.sku`, `CartOrder.oid` là ShortUUID — dùng trong URL thay cho khóa
  chính số.
- **Tiền tệ:** `DecimalField(max_digits=20, decimal_places=2)`, đơn vị VND.
- **Xóa mềm:** `core_category`, `core_vendor`, `core_product`, `core_coupon` mang
  cặp cờ `is_deleted` / `deleted_at`.
- **Trạng thái sản phẩm:** `draft | disabled | in_review | rejected | published`.

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
| Triển khai | Nền tảng PaaS đám mây |
| CSDL đám mây | Serverless Postgres |
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

> **Nợ thiết kế:** các mục trên mới là bảng tóm tắt kế thừa từ TLCN, chưa được
> kiểm chứng lại với mã nguồn, và chưa có sơ đồ thiết kế. Rubric yêu cầu ≥ 4 loại
> sơ đồ khớp với mã nguồn để đạt Mức 5 ở TC2.1. Xem [`PLAN.md`](PLAN.md) P-24.

---

## 4. Lịch sử chỉnh sửa

Nhật ký các lần sửa file này được ghi chung với `SRS.md` tại [`PLAN.md`](PLAN.md)
§6. Khi sửa bất kỳ mục nào ở trên, thêm một dòng vào bảng đó: sửa gì, vì sao, và
commit tương ứng.
