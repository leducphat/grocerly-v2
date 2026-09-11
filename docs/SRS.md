# SRS — Grocerly

*Đặc tả yêu cầu phần mềm (Software Requirements Specification)*

**Đề tài:** Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng
**Sinh viên:** Lê Đức Phát — 21139083 · **GVHD:** Hoàng Văn Dũng
**Đơn vị:** Trường ĐH Công nghệ Kỹ thuật TP.HCM — Khoa CNTT — Bộ môn Công nghệ Phần mềm

| | |
|---|---|
| Trạng thái | **Tài liệu sống** — mở cho chỉnh sửa |
| Nguồn gốc | Chuyển thể từ báo cáo TLCN `CLC_CNPM_1_LEDUCPHAT.pdf` |
| Cập nhật | 11/09/2026 |

> **Phạm vi của tài liệu này.** Đây là *spec of record* của sản phẩm — mô tả hệ
> thống **phải đúng như hiện trạng mã nguồn**, không phải như báo cáo cũ đã viết.
>
> Nội dung ban đầu lấy từ đặc tả TLCN, nhưng đặc tả đó **có thể sai hoặc đã lỗi
> thời**. Phát hiện chỗ nào lệch thì sửa file này cho đúng, và ghi lại lần sửa đó
> trong [`PLAN.md`](PLAN.md) §6 (Nhật ký chỉnh sửa đặc tả) kèm lý do.
>
> Lý do phải ghi lại: tại buổi bảo vệ, hội đồng đối chiếu ngẫu nhiên sơ đồ và đặc
> tả với mã nguồn. Một đặc tả sai bị giữ lại vì "báo cáo cũ viết vậy" sẽ thành
> điểm trừ, trong khi một đặc tả đã sửa kèm lý do rõ ràng lại là minh chứng cho
> thấy sinh viên làm chủ hệ thống.

> **Về ranh giới SRS / SDD — sẽ tách.** Đúng chuẩn thì SRS chỉ chứa *yêu cầu*
> (Mục 1–6: bối cảnh, mục tiêu, tác nhân, FR, NFR, use case), còn mô hình dữ liệu,
> giao diện và công nghệ (Mục 7–9) thuộc về **SDD** — tài liệu đặc tả thiết kế.
>
> File này **tạm thời gộp cả hai**, và sẽ được tách thành `SRS.md` + `SDD.md`
> ngay trong Giai đoạn 0, *trước* khi rà soát nội dung — xem [`PLAN.md`](PLAN.md)
> P-07 và quyết định D-011. Tách sớm để lịch sử Git của mỗi tài liệu ghi lại trọn
> vẹn quá trình rà soát của riêng nó.

---

## 1. Bối cảnh và lý do chọn đề tài

Thương mại điện tử tại Việt Nam đang tăng trưởng mạnh, người tiêu dùng chuyển
dịch sang mua sắm trực tuyến cả với nhu yếu phẩm và thực phẩm hằng ngày. Tuy
nhiên các nền tảng bán lẻ thực phẩm hiện tại còn hai nhóm bất cập:

- **Phía quản lý:** kiểm soát hàng hóa, cập nhật hạn sử dụng và thống kê doanh
  thu phần lớn vẫn thủ công.
- **Phía người tiêu dùng:** khó tìm đúng sản phẩm giữa hàng ngàn mặt hàng; thiếu
  nhân sự tư vấn trực tuyến khiến thắc mắc không được giải đáp kịp thời, làm gián
  đoạn trải nghiệm và giảm tỷ lệ chuyển đổi.

Grocerly giải quyết vấn đề bằng một nền tảng thương mại điện tử chuyên biệt cho
ngành hàng thực phẩm, tích hợp **Trợ lý ảo AI** đóng vai trò nhân viên tư vấn
24/7: giao tiếp bằng ngôn ngữ tự nhiên, gợi ý và tìm sản phẩm, hỗ trợ thêm hàng
vào giỏ và hoàn tất thanh toán chỉ qua vài dòng tin nhắn.

### 1.1 Khảo sát hệ thống liên quan

| Hệ thống | Ưu điểm | Khuyết điểm |
|---|---|---|
| **Bách Hóa Xanh** | Giao diện thân thiện, phân loại danh mục chi tiết; chọn khung giờ giao linh hoạt; cập nhật tồn kho theo khu vực địa lý | Tải trang chậm giờ cao điểm; gợi ý sản phẩm thay thế chưa thông minh; **không có AI Chatbot** |
| **Co.opmart (Co.op Online)** | Uy tín thương hiệu; tích điểm thành viên đồng bộ online–offline; nhiều combo và khuyến mãi theo sự kiện | Giao diện web cứng nhắc, trải nghiệm mobile chưa mượt; bộ lọc theo thuộc tính hạn chế; **không có AI Chatbot** |
| **Shopee** | Hệ sinh thái lớn, thao tác mượt; gợi ý theo lịch sử mua sắm tốt; mã giảm giá và Flash Sale hấp dẫn | Thiếu hàng thực phẩm tươi sống; giao hàng 2–3 ngày qua trung gian, không phù hợp nhu cầu dùng trong ngày; **AI Chatbot chỉ có trên app, bản web không hỗ trợ** |

**Khoảng trống đề tài nhắm tới:** không nền tảng nào trong ba nền tảng trên cung
cấp trợ lý AI hội thoại trên web có khả năng *thao tác thay người dùng* (tìm →
thêm giỏ → dẫn tới thanh toán).

---

## 2. Mục tiêu và phạm vi

### 2.1 Mục tiêu

1. Thiết kế và xây dựng giao diện website mua sắm trực quan, thân thiện, tối ưu
   trải nghiệm người dùng (UX/UI).
2. Phát triển hệ thống chức năng cốt lõi của một nền tảng TMĐT: tìm kiếm và lọc
   sản phẩm, quản lý giỏ hàng, đặt hàng và thanh toán trực tuyến an toàn.
3. Nghiên cứu và tích hợp Trợ lý ảo AI (Chatbot) nhằm tự động hóa chăm sóc khách
   hàng, hỗ trợ tìm sản phẩm và tương tác mua sắm qua hội thoại ngôn ngữ tự nhiên.
4. Cung cấp công cụ quản trị (Dashboard) tập trung cho quản trị viên và nhân viên cửa hàng:
   quản lý kho, xử lý đơn hàng, quản lý người dùng, theo dõi báo cáo doanh thu.

### 2.2 Phạm vi

- Nền tảng TMĐT đặc thù cho ngành hàng nhu yếu phẩm và thực phẩm (Grocery).
- Tích hợp dịch vụ bên thứ ba: Google Gemini AI, cổng thanh toán VNPay, nền tảng
  triển khai đám mây, dịch vụ cơ sở dữ liệu đám mây, dịch vụ lưu trữ đa phương tiện.
- Mô hình **một nhà bán** (D-015): một cửa hàng duy nhất bán hàng của nhiều nhà
  cung cấp. "Nhà cung cấp" chỉ là thông tin nguồn hàng gắn với sản phẩm, không
  phải tài khoản người bán.
- Phân quyền cho **4 nhóm tác nhân**: Khách vãng lai (Guest), Khách hàng
  (Customer), Nhân viên cửa hàng (Staff), Quản trị viên (Admin).

### 2.3 Ngoài phạm vi

Các mục dưới đây **không thuộc phạm vi KLTN**; chúng được ghi nhận ở mục "Các
hướng phát triển mở rộng" cuối báo cáo: tìm kiếm full-text và gợi ý từ khóa; thống
kê đa chiều nâng cao; live chat thời gian thực giữa khách và cửa hàng; mô hình nhiều
người bán (marketplace); gợi ý sản
phẩm bằng Machine Learning; ứng dụng di động iOS/Android.

KLTN tập trung làm chắc phần cốt lõi đã có — xem [`PLAN.md`](PLAN.md) §1.

---

## 3. Tác nhân (Actors)

| Mã | Tác nhân | Mô tả |
|---|---|---|
| A1 | **Khách vãng lai** (Guest) | Chưa đăng nhập; duyệt và tìm sản phẩm, tương tác AI, đăng ký tài khoản |
| A2 | **Khách hàng** (Customer) | Đã đăng ký; mua hàng, quản lý hồ sơ, yêu thích, đánh giá |
| A3 | **Nhân viên cửa hàng** (Staff) | Vận hành cửa hàng qua `/useradmin/`: sản phẩm, tồn kho, đơn hàng, thống kê của cửa hàng |
| A4 | **Quản trị viên** (Admin / Superuser) | Toàn quyền: duyệt sản phẩm, danh mục, người dùng, mã giảm giá, giám sát toàn hệ thống |

---

## 4. Yêu cầu chức năng

### 4.1 Khách vãng lai (A1)

| Mã | Yêu cầu |
|---|---|
| FR-G-01 | Truy cập website, xem danh mục sản phẩm, tìm sản phẩm theo tên hoặc loại hàng hóa |
| FR-G-02 | Xem thông tin chi tiết sản phẩm: giá, mô tả, hình ảnh, đánh giá từ người dùng khác |
| FR-G-03 | Tương tác với Trợ lý ảo AI để được tư vấn, tìm sản phẩm theo nhu cầu |
| FR-G-04 | Đăng ký tài khoản mới để trở thành người dùng chính thức |

### 4.2 Khách hàng (A2)

| Mã | Yêu cầu |
|---|---|
| FR-C-01 | Đăng nhập, đăng xuất, đổi mật khẩu, quản lý hồ sơ cá nhân (Avatar, Bio) |
| FR-C-02 | Thêm sản phẩm yêu thích; thêm vào giỏ hàng, cập nhật số lượng, xóa khỏi giỏ |
| FR-C-03 | Nhờ Trợ lý ảo AI thêm hàng vào giỏ tự động và hướng dẫn thanh toán |
| FR-C-04 | Đặt hàng, áp dụng mã khuyến mãi còn hiệu lực; thanh toán trực tuyến (VNPay) hoặc COD |
| FR-C-05 | Theo dõi tình trạng đơn hàng, xem lịch sử mua sắm và hóa đơn chi tiết trên Dashboard cá nhân |
| FR-C-06 | Đánh giá, bình luận và cho điểm sản phẩm sau khi đơn hàng giao dịch thành công |

### 4.3 Nhân viên cửa hàng (A3)

| Mã | Yêu cầu |
|---|---|
| FR-V-01 | Đăng nhập vào khu vực quản lý cửa hàng |
| FR-V-02 | Quản lý sản phẩm: thêm mới, cập nhật giá bán, số lượng tồn kho, đăng tải hình ảnh, xóa hoặc ẩn |
| FR-V-03 | Quản lý đơn hàng: tiếp nhận đơn, thay đổi trạng thái giao hàng (đã đóng gói, đang giao…) |
| FR-V-04 | Thống kê cá nhân: biểu đồ doanh thu, số lượng đơn, tình trạng hàng hóa của cửa hàng theo thời gian thực |

### 4.4 Quản trị viên (A4)

| Mã | Yêu cầu |
|---|---|
| FR-A-01 | Đăng nhập an toàn vào trang quản trị bằng tài khoản Superuser |
| FR-A-02 | Duyệt và kiểm soát sản phẩm do nhân viên đăng; xóa mềm hoặc vô hiệu hóa sản phẩm vi phạm |
| FR-A-03 | Quản lý danh mục: thêm, sửa, xóa danh mục hàng hóa dùng chung toàn hệ thống |
| FR-A-04 | Quản lý người dùng: tra cứu, phân quyền, khóa tài khoản vi phạm, xóa vĩnh viễn |
| FR-A-05 | Quản lý mã giảm giá: khởi tạo, thiết lập phần trăm giảm, phân phối tới khách hàng |
| FR-A-06 | Giám sát toàn hệ thống: truy xuất, kiểm tra toàn bộ đơn hàng của cửa hàng |

---

## 5. Yêu cầu phi chức năng

| Mã | Nhóm | Yêu cầu |
|---|---|---|
| NFR-01 | **UI/UX** | Giao diện đáp ứng (responsive), hiển thị đúng và ổn định trên mọi kích thước màn hình |
| NFR-02 | **Hiệu năng** | Xử lý được lượng lớn truy cập đồng thời; thời gian phản hồi từ máy chủ nhanh, không làm gián đoạn trải nghiệm |
| NFR-03 | **Bảo mật** | Mật khẩu bắt buộc mã hóa trước khi lưu; giao dịch thanh toán qua kênh mã hóa SSL/TLS; có cơ chế ngăn chặn SQL Injection và XSS |
| NFR-04 | **Khả năng mở rộng & bảo trì** | Mã nguồn tổ chức theo kiến trúc MVT của Django, thiết kế thành module rời rạc để dễ bảo trì, gỡ lỗi, nâng cấp |

> ⚠️ **Ghi chú cho KLTN:** bốn NFR trên là mô tả định tính. Rubric KLTN yêu cầu
> **≥ 5 yêu cầu phi chức năng có ràng buộc định lượng** để đạt Mức 5 ở TC2.1.
> Việc định lượng hóa được theo dõi ở [`PLAN.md`](PLAN.md) (P-21); khi chốt cùng
> GVHD thì sửa thẳng bảng trên và ghi lần sửa vào `PLAN.md` §6.

---

## 6. Danh sách Use Case

26 use case đã đặc tả trong TLCN (mỗi UC có Short Description, Actors,
Pre-/Post-Conditions, Main Flow, Alternate Flow, Exception Flow).

| Mã | Use Case | Tác nhân |
|---|---|---|
| UC-01 | Đăng ký | A1 |
| UC-02 | Đăng nhập | A2, A3, A4 |
| UC-03 | Xem danh sách sản phẩm | A1, A2 |
| UC-04 | Xem chi tiết sản phẩm | A1, A2 |
| UC-05 | Tìm kiếm & Lọc | A1, A2 |
| UC-06 | Quản lý Giỏ hàng (CRUD) | A1, A2 |
| UC-07 | Đổi Ngôn ngữ | A1, A2 |
| UC-08 | Gửi Liên hệ | A1, A2 |
| UC-09 | Thanh toán & Đặt hàng | A2 |
| UC-10 | Đăng xuất | A2, A3, A4 |
| UC-11 | Cập nhật Hồ sơ (xem/sửa/đổi mật khẩu) | A2 |
| UC-12 | Quản lý Yêu thích | A2 |
| UC-13 | Lịch sử Đơn mua | A2 |
| UC-14 | Đánh giá Sản phẩm (CRUD) | A2 |
| UC-15 | Tương tác Trợ lý AI | A1, A2 |
| UC-16 | Nhờ AI Tìm sản phẩm | A1, A2 |
| UC-17 | Nhờ AI Thêm vào Giỏ | A1, A2 |
| UC-18 | Nhờ AI Hướng dẫn thanh toán | A1, A2 |
| UC-19 | Quản lý Sản phẩm | A3, A4 |
| UC-20 | Quản lý Đơn hàng | A3, A4 |
| UC-21 | Quản lý Mã giảm giá | A4 |
| UC-22 | Quản lý Người dùng | A4 |
| UC-23 | Quản lý Danh mục | A4 |
| UC-24 | Quản lý Toàn bộ sản phẩm (duyệt/gỡ) | A4 |
| UC-25 | Quản lý Toàn bộ Đơn hàng | A4 |
| UC-26 | Xem báo cáo thống kê | A3, A4 |

### 6.1 Ràng buộc nghiệp vụ đáng chú ý

- **UC-06:** cập nhật số lượng lớn hơn tồn kho thực tế → báo lỗi và reset về số
  lượng hợp lệ.
- **UC-14:** chỉ đánh giá được sản phẩm đã mua (đơn ở trạng thái `Shipped`); cố
  đánh giá sản phẩm chưa mua → nút bị vô hiệu hóa.
- **UC-19:** sản phẩm do nhân viên tạo lưu ở trạng thái `in_review`, phải được
  Admin duyệt sang `published` mới hiển thị cho khách.
- **UC-20:** **không có thao tác xóa đơn hàng** — lịch sử giao dịch phải được giữ
  lại; đơn đã `Delivered` không đổi được trạng thái.
- **UC-23:** xóa danh mục đang chứa nhiều sản phẩm → cảnh báo sản phẩm sẽ bị mồ
  côi (Uncategorized).
- **UC-25:** Admin không được xóa vĩnh viễn đơn hàng, để phục vụ đối soát kế toán.
- **UC-17:** AI chỉ thêm vào giỏ khi sản phẩm còn hàng; hết hàng → AI từ chối.
- **UC-18:** giỏ trống → AI nhắc thêm hàng trước khi thanh toán.

> **Nợ đặc tả:** các UC trên chưa có *acceptance criteria* dạng kiểm chứng được.
> Rubric yêu cầu 100% use case có AC để đạt Mức 5 ở TC2.1. Xem [`PLAN.md`](PLAN.md).

---

## 7. Mô hình dữ liệu

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

### 7.1 Quy ước dữ liệu

- **Định danh công khai:** `Category.c_id`, `Vendor.v_id`, `Product.p_id`,
  `Product.sku`, `CartOrder.oid` là ShortUUID — dùng trong URL thay cho khóa
  chính số.
- **Tiền tệ:** `DecimalField(max_digits=20, decimal_places=2)`, đơn vị VND.
- **Xóa mềm:** `core_category`, `core_vendor`, `core_product`, `core_coupon` mang
  cặp cờ `is_deleted` / `deleted_at`.
- **Trạng thái sản phẩm:** `draft | disabled | in_review | rejected | published`.

---

## 8. Danh sách giao diện

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

## 9. Công nghệ và dịch vụ tích hợp

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

### 9.1 Thiết kế Trợ lý AI

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

---

## 10. Kiểm thử

Phương pháp: kiểm thử hộp đen (Black-box), dựa trên yêu cầu chức năng và giao diện.

| Mã | Kịch bản | Kết quả mong đợi | Trạng thái |
|---|---|---|---|
| TC_01 | Đăng nhập email + mật khẩu đúng | Đăng nhập thành công, chuyển về trang chủ | PASS |
| TC_02 | Đăng nhập sai mật khẩu | Báo lỗi "Email hoặc mật khẩu không chính xác" | PASS |
| TC_03 | Đăng ký với thông tin hợp lệ | Tạo tài khoản, chuyển về trang chủ đã đăng nhập | PASS |
| TC_04 | Đăng ký trùng email | Báo lỗi "Email này đã được sử dụng" | PASS |
| TC_05 | Thêm giỏ → điền địa chỉ → đặt hàng (COD) | Đơn lưu vào CSDL, chuyển trang thành công, giỏ được làm sạch | PASS |

> ⚠️ **Ghi chú cho KLTN:** toàn bộ 5 test case trên là **thủ công**. Chưa có kiểm
> thử tự động, chưa có báo cáo độ phủ. Đây là khoảng trống lớn nhất so với rubric
> — xem [`PLAN.md`](PLAN.md).

---

## 11. Hạn chế đã ghi nhận

Trích nguyên trạng từ phần Kết luận của TLCN:

1. Biểu đồ thống kê cho người bán và quản trị viên còn đơn giản, chưa đa dạng
   chiều phân tích dữ liệu.
2. Tìm kiếm mới ở mức theo tên và lọc theo danh mục cơ bản; chưa có full-text
   search hay gợi ý thông minh.
3. Chưa có tương tác thời gian thực (live chat giữa khách hàng và người bán).
4. Hệ gợi ý sản phẩm dựa trên tiêu chí tĩnh (nổi bật, ngẫu nhiên), chưa học theo
   hành vi người dùng.

---

## 12. Lịch sử chỉnh sửa đặc tả

Nhật ký các lần sửa file này được ghi tập trung tại [`PLAN.md`](PLAN.md) §6, để
việc chỉnh đặc tả nằm cùng chỗ với việc theo dõi tiến độ thay vì tách làm hai nơi.

Khi sửa bất kỳ mục nào ở trên, thêm một dòng vào bảng đó: sửa gì, vì sao, và commit
tương ứng.
