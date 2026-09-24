# BẢN CAM KẾT SẢN PHẨM — Grocerly (KLTN)

> **⚠️ BẢN NHÁP — chưa ký.** Soạn ngày 10/09/2026 để trao đổi với GVHD. Phần
> chức năng (§2) đã đối chiếu với mã nguồn; phần metric và KPI (§5) mới có mục
> chất lượng mã nguồn (§5.1, soạn ngày 24/09/2026).

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
| CN-08 | Giỏ hàng: thêm, cập nhật số lượng, xóa; không cho vượt tồn kho | UC-06 | ✅ Khớp — L-7 đã sửa 21/09/2026 |
| CN-09 | Đổi ngôn ngữ vi ↔ en | UC-07 | Có |
| CN-10 | Gửi liên hệ tới ban quản trị | UC-08 | Có |
| CN-11 | Thanh toán: nhập thông tin giao hàng, áp mã giảm giá, chọn COD hoặc VNPay | UC-09 | ✅ Khớp — L-6, L-8 đã sửa 21/09/2026 |
| CN-12 | Cập nhật hồ sơ cá nhân, đổi mật khẩu | UC-11 | Có |
| CN-13 | Danh sách yêu thích: thêm, xem, xóa | UC-12 | Có |
| CN-14 | Xem lịch sử đơn mua và chi tiết từng đơn; đặt địa chỉ mặc định | UC-13 | Có |
| CN-15 | Đánh giá và chấm điểm sản phẩm (1–5 sao) | UC-14 | ✅ Khớp — L-3 đã sửa, L-4 chốt sửa đặc tả 23/09/2026 |

### 2.2 Trợ lý AI

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-16 | Hỏi đáp, tư vấn bằng ngôn ngữ tự nhiên | UC-15 | Có |
| CN-17 | AI tìm sản phẩm còn hàng theo nhu cầu | UC-16 | ✅ Khớp — L-10 đã sửa 22/09/2026 |
| CN-18 | AI đề xuất thêm vào giỏ — chỉ thêm khi người dùng xác nhận | UC-17 | ✅ Khớp — L-9 đã sửa 22/09/2026 |
| CN-19 | AI dẫn người dùng tới trang thanh toán | UC-18 | Có |

*Công cụ `get_bestsellers` (gợi ý sản phẩm "nổi bật") vẫn còn trong mã nguồn nhưng
**không thuộc cam kết**: nó chỉ lấy sản phẩm gắn cờ `featured` thủ công, không tính
doanh số thật.*

### 2.3 Nhân viên cửa hàng — `/useradmin/`

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-20 | Dashboard: doanh thu, doanh thu theo tháng, số đơn, khách hàng mới | UC-26 | Có |
| CN-21 | Quản lý sản phẩm: thêm, sửa, xóa mềm, cập nhật tồn kho, quản lý ảnh | UC-19 | ✅ Khớp — L-1, L-2 chốt sửa đặc tả |
| CN-22 | Quản lý đơn hàng: xem, đổi trạng thái giao hàng; không có thao tác xóa đơn | UC-20 | ✅ Khớp — L-5 đã sửa 23/09/2026 |
| CN-23 | Xem danh sách đánh giá; cập nhật hồ sơ và đổi mật khẩu nhân viên | *(chưa có UC)* | Có |

### 2.4 Quản trị viên — Django admin

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-24 | Quản lý mã giảm giá: tạo, sửa, bật/tắt, xóa mềm và khôi phục | UC-21 | Có |
| CN-25 | Quản lý người dùng: tra cứu, phân quyền, khóa tài khoản | UC-22 | Có |
| CN-26 | Quản lý danh mục: thêm, sửa, xóa mềm và khôi phục | UC-23 | Có |
| CN-27 | Quản lý toàn bộ sản phẩm: đổi trạng thái hiển thị, xóa mềm và khôi phục | UC-24 | ✅ Khớp — L-2 chốt sửa đặc tả |
| CN-28 | Tra cứu toàn bộ đơn hàng, lọc theo trạng thái thanh toán và giao hàng | UC-25 | Có |
| CN-29 | Quản lý nhà cung cấp: thêm, sửa, xóa mềm và khôi phục | *(chưa có UC)* | Có |
| CN-30 | Xem hộp thư liên hệ | *(chưa có UC)* | Có |

**Tổng: 30 chức năng** — cả 30 khớp giữa đặc tả và mã nguồn từ 23/09/2026: tám
chỗ `Lệch` ban đầu đã xử lý hết (§3). Các chức năng CN-03, 07, 23, 29, 30 có
trong mã nguồn nhưng đặc tả TLCN chưa có use case; sẽ bổ sung UC ở P-23.

---

## 3. Những chỗ lệch giữa đặc tả TLCN và mã nguồn

Mỗi chỗ có hai cách: **sửa đặc tả** cho khớp code, hoặc **sửa code** cho khớp đặc
tả. Cột cuối giữ lại đề xuất ban đầu và ghi cách đã chốt, để đọc lại được cả lúc
bảo vệ.

| Mã | Đặc tả TLCN nói | Mã nguồn thực tế | Đề xuất |
|---|---|---|---|
| **L-1** | Người bán quản lý **gian hàng riêng**, thống kê của riêng gian hàng (A3, FR-V-04) | Không có vai trò người bán riêng: ai có `is_staff` đều vào `/useradmin/` và thấy **toàn bộ** sản phẩm, đơn hàng, doanh thu (`useradmin/views.py`) | ✅ **Đã chốt — sửa đặc tả** (D-015): mô hình một nhà bán, A3 là *nhân viên cửa hàng*. `SRS.md` đã sửa ngày 11/09/2026 |
| **L-2** | Sản phẩm người bán tạo ở trạng thái `in_review`, Admin duyệt sang `published` mới hiển thị (UC-19, UC-24) | `add_product` gán thẳng `product_status = 'published'` — không có bước duyệt | ✅ **Đã chốt 23/09/2026 — sửa đặc tả** (D-028): bước duyệt sinh ra cho mô hình nhiều người bán mà D-015 đã bỏ; nhân viên của chính cửa hàng duyệt hàng của mình thì không có nghĩa nghiệp vụ. `SRS.md` §6.1 và FR-A-02 đã sửa; Admin vẫn ẩn hoặc gỡ bán được sản phẩm |
| **L-3** | Chỉ đánh giá được sản phẩm **đã mua** (đơn `Shipped`) (UC-14) | Chỉ kiểm tra "chưa từng đánh giá sản phẩm này"; `ajax_add_review` không kiểm tra đăng nhập, không kiểm tra đã mua | ✅ **Đã sửa 23/09/2026** (D-027). `ajax_add_review` có `@login_required` và hàm `has_received_product` hỏi `CartOrderItem` xem khách có đơn nào chứa sản phẩm này ở trạng thái `shipped` hoặc `delivered` chưa; chưa mua thì 403, đã đánh giá rồi cũng 403, dữ liệu sai thì 400 qua `ProductReviewForm`. `product_detail_view` dùng chính hàm đó cho `make_review` nên giao diện và máy chủ cùng một điều kiện. Đặc tả nhận thêm trạng thái `Delivered` (`PLAN.md` §6 dòng 11). Thêm `core/tests/test_reviews.py`, chín test |
| **L-4** | Đánh giá có đủ CRUD (UC-14) | Khách chỉ **tạo** được; sửa/xóa chỉ làm được trong Django admin | ✅ **Đã chốt 23/09/2026 — sửa đặc tả** (D-028): khách tạo đánh giá, quản trị viên kiểm duyệt trong Django admin. Bỏ chữ "(CRUD)" ở UC-14 |
| **L-5** | Đơn đã `Delivered` không được đổi trạng thái nữa (UC-20) | `change_order_status` không chặn — đổi được từ bất kỳ trạng thái nào | ✅ **Đã sửa 23/09/2026** (D-026). `change_order_status` chặn hai điều kiện trước khi ghi: trạng thái gửi lên phải thuộc `STATUS_CHOICES`, và đơn đã `delivered` thì không đổi nữa. Viết test mới lộ thêm một đường vào: ô chọn trên giao diện có dòng nhắc `value="pending"`, bấm Save khi chưa chọn gì là đơn rơi vào trạng thái không tồn tại — đã đổi sang `value=""`. Thêm `useradmin/tests/`, sáu test |
| **L-6** 🔴 | *(đặc tả không nói tới — mặc định giá lấy từ hệ thống)* | **Giá do trình duyệt gửi lên.** `add_to_cart` lưu `price` từ tham số GET vào session; `save_checkout_info` tính `order.price` từ giá đó; số tiền gửi sang VNPay là `order.price`. Khách sửa tham số là đặt được hàng với giá tùy ý. Tiền còn tính bằng `float` thay vì `Decimal` | ✅ **Đã sửa 21/09/2026** (D-022). Thêm `_refresh_cart` trong `core/views.py`: mọi lần đụng tới giỏ đều ghi đè giá trong session bằng giá đọc từ `Product` và cộng tổng bằng `Decimal`; `save_checkout_info` lấy tổng từ chính hàm đó. `/add-to-cart/` chỉ còn nhận `id` và `qty`, JavaScript thôi gửi giá lên. Test `test_order_total_uses_product_price_not_price_sent_by_browser` đã gỡ `xfail` |
| **L-7** | Cập nhật số lượng lớn hơn tồn kho → báo lỗi, reset về số hợp lệ (UC-06) | `add_to_cart`, `update_cart` và `save_checkout_info` không kiểm tra tồn kho ở server | ✅ **Đã sửa 21/09/2026** (D-024). `_refresh_cart` đọc thêm `stock_count`: dòng giỏ xin nhiều hơn tồn kho bị hạ xuống bằng tồn kho kèm `messages.warning`, sản phẩm hết hàng thì dòng đó rời khỏi giỏ. `add_to_cart` gọi `_refresh_cart` trước khi trả JSON nên cả ba lối vào — thêm giỏ, sửa số lượng, tạo đơn — đều qua một chỗ kiểm tra. Đặc tả đổi từ "báo lỗi" sang "hạ số lượng và báo" (`SRS.md` §6.1). Test `test_add_to_cart_does_not_keep_quantity_above_stock` đã gỡ `xfail` |
| **L-8** 🔴 | *(đặc tả không nói tới — mặc định đơn thanh toán online chỉ thành "đã thanh toán" khi VNPay xác nhận)* | `payment_completed_view` tự đặt `paid_status = True` cho đơn `online` chưa thanh toán. Khách tạo đơn xong, mở thẳng `/payment-completed/<oid>/` là đơn thành đã thanh toán mà không qua VNPay. *Phát hiện 16/09/2026 khi viết test (P-12)* | ✅ **Đã sửa 21/09/2026** (D-023). `payment_completed_view` không còn ghi `paid_status`; chỉ `vnpay_return` / `vnpay_ipn` (đã kiểm chữ ký) đổi được trạng thái này. Đơn online chưa được VNPay xác nhận mà mở trang hoàn tất thì bị đưa về `core:checkout` kèm nhắc thanh toán, thay vì thấy màn hình thanh toán thành công. Test `test_payment_completed_page_does_not_mark_unpaid_order_as_paid` đã gỡ `xfail` |
| **L-9** | AI chỉ thêm vào giỏ khi sản phẩm còn hàng; hết hàng → AI từ chối (UC-17, SRS §6.1) | `ai_chat` xử lý `request_add_to_cart` bằng `Product.objects.filter(p_id=...)`, không kiểm tra `in_stock` / `stock_count` — AI vẫn đề nghị thêm sản phẩm đã hết hàng. *Phát hiện 16/09/2026 (P-12)* | ✅ **Đã sửa 22/09/2026** (D-025). Nhánh `request_add_to_cart` tìm sản phẩm qua `published_products()` rồi tách hai trường hợp: không tìm thấy trả `Product not found`, tồn kho bằng 0 trả `Product is out of stock` để Gemini nói đúng lý do. Test `test_ai_add_to_cart_refuses_out_of_stock_product` đã gỡ `xfail`, có thêm khẳng định về lý do gửi cho Gemini |
| **L-10** | Sản phẩm bị vô hiệu hóa không hiển thị với khách (FR-A-02, UC-24) | Trang cửa hàng lọc theo `product_status = 'published'`; công cụ AI `search_products`, `get_bestsellers` và API `/api/v1/products/` lại lọc theo cờ khác là `status = True`, bỏ qua `product_status` → sản phẩm đã ẩn khỏi cửa hàng vẫn được AI tìm thấy. *Phát hiện 16/09/2026 (P-12)* | ✅ **Đã sửa 22/09/2026** (D-025). `store_api/views.py` có `published_products()` (`product_status='published'`, đúng điều kiện các trang cửa hàng dùng) và `buyable_products()` (lọc thêm `stock_count > 0`); công cụ tìm kiếm, hàng bán chạy và `/api/v1/products/` đều gọi hàm này. Vai trò cờ `status`: **không còn chỗ nào đọc** — cùng với `in_stock`, đây là hai cột không form nào ghi nên luôn bằng `True`; đã ghi chú tại `core/models.py`, không xóa cột. Test `test_search_tool_does_not_return_product_hidden_from_store` đã gỡ `xfail`; thêm file `store_api/tests/test_product_api.py` cho API |

**Mười chỗ lệch đều đã chốt.** Ba chỗ chốt bằng cách sửa đặc tả — L-1 (11/09/2026,
D-015), L-2 và L-4 (23/09/2026, D-028) — vì chúng mô tả mô hình nhiều người bán
không còn áp dụng. Bảy chỗ còn lại chốt bằng cách sửa code: L-6, L-7, L-8
(21/09/2026), L-9, L-10 (22/09/2026), L-3 và L-5 (23/09/2026). Mỗi lần sửa đặc tả
ghi vào `PLAN.md` §6; mỗi lần sửa code có test đi kèm, và bộ test không còn `xfail`
nào. L-3 và L-5 không có test tái hiện sẵn từ P-12 nên được viết test trước, chạy cho
đỏ, rồi mới sửa.

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

## 5. Metric và KPI — *đang soạn*

### 5.1 Chất lượng mã nguồn (TC2.4)

Ba con số của TC2.4 đều đo bằng công cụ chạy trong CI ở mỗi lần đẩy mã nguồn, nên
có số đo cho từng commit chứ không chỉ một lần cuối kỳ. Ngưỡng đề xuất giữ đúng Mức
5 của rubric, vì số đo hiện tại đã đạt.

| Metric | Công cụ và cách đo | Ngưỡng | Số đo 24/09/2026 |
|---|---|---|---|
| Lỗi lint | Ruff, bộ luật ghi trong `grocerly/ruff.toml` | 0 | 0 (30 trước khi sửa) |
| Issue Blocker/Critical | Ruff, quy đổi theo danh sách dưới đây | 0 | 0 (5 trước khi sửa) |
| Tỉ lệ dòng trùng lặp | jscpd, trên mã Python của ứng dụng | ≤ 3% | 1,09% |

**Quy đổi Blocker/Critical.** Ruff không chia mức nghiêm trọng, mọi vi phạm đều là
một lỗi như nhau. Rubric cũng không định nghĩa hai mức này, nên đồ án quy đổi theo
định nghĩa của SonarQube: Blocker là lỗi nhiều khả năng làm ứng dụng hỏng khi chạy,
Critical là lỗi ít khả năng hơn hoặc là lỗ hổng bảo mật.

- Blocker: code không chạy được. Gồm lỗi cú pháp (`E9`), dùng tên chưa định nghĩa
  hoặc biến chưa gán (`F821`, `F822`, `F823`), câu lệnh đặt sai chỗ như `return`
  ngoài hàm (`F7`).
- Critical: lỗ hổng bảo mật theo bộ luật bandit (`S`), và `except:` trần bắt mọi
  lỗi rồi nuốt đi (`E722`).
- Các luật còn lại trong `ruff.toml`, như import thừa, quy ước Django và các mẫu dễ
  gây lỗi của bugbear, chỉ tính là lỗi lint.

CI đòi 0 lỗi trên mọi luật đã bật, nên lần chạy nào xanh cũng là 0 Blocker/Critical.
Năm issue trước khi sửa gồm bốn chỗ in ảnh trong trang quản trị bằng `mark_safe`
(`S308`) và một `except:` trần ở trang đăng nhập.

**Phạm vi đo trùng lặp.** Tính mã Python của ứng dụng, không tính migration vì do
Django sinh ra, và không tính test vì test lặp lại cấu trúc chuẩn bị - thực hiện -
kiểm tra một cách có chủ ý. Template HTML không tính vào con số trên, vì các công cụ
rubric nêu tên đều đo mã của ngôn ngữ lập trình, còn template ở đây phần lớn là HTML
chép từ bộ giao diện mẫu dùng từ thời TLCN. Để không che con số đó đi, số đo của
template ghi luôn ở đây: 49 file, 7.704 dòng, trùng 26,6%. Con số này đo sau khi xóa
13 trang mẫu của bộ giao diện, khoảng 22.400 dòng, mà không trang nào của cửa hàng
dùng tới; tính cả chúng thì là 78,6%. Phần trùng trong template ghi là hạn chế,
không cam kết ngưỡng.

Kiểm tra lại được bằng hai lệnh chạy trong `grocerly/`: `ruff check .` và `jscpd .`.

### 5.2 Các phần còn lại

Sẽ bổ sung trước khi trình ký. Khung dự kiến:

- **KPI nghiệp vụ** (TC1 Mức 5 cần ≥ 5, định lượng): ví dụ tỉ lệ đặt hàng thành
  công qua trợ lý AI, số bước từ tìm sản phẩm tới đặt hàng, thời gian phản hồi
  của trợ lý…
- **Metric kỹ thuật** theo rubric Mục 5 — độ phủ test, số chặng CI/CD, số lần
  deploy, tỉ lệ build xanh, lỗi lint, secret lộ, người dùng thực nghiệm, SUS.
  Rubric cho phép điều chỉnh ngưỡng tại bước này.
- **Cách hiểu "Pull Request có review" cho đồ án một người** (D-016, giữ nguyên
  cách hiểu của D-012).
- **Cách lấy ý kiến bên liên quan** gộp vào thực nghiệm người dùng (D-013).

---

## 6. Xác nhận

| Sinh viên | Giảng viên hướng dẫn |
|---|---|
| | |
| Lê Đức Phát | Hoàng Văn Dũng |
| Ngày: | Ngày: |
