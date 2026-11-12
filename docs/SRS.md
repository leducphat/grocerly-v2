# SRS — Grocerly

*Đặc tả yêu cầu phần mềm (Software Requirements Specification)*

**Đề tài:** Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng
**Sinh viên:** Lê Đức Phát — 21139083 · **GVHD:** Hoàng Văn Dũng
**Đơn vị:** Trường ĐH Công nghệ Kỹ thuật TP.HCM — Khoa CNTT — Bộ môn Công nghệ Phần mềm

| | |
|---|---|
| Trạng thái | **Tài liệu sống** — mở cho chỉnh sửa |
| Nguồn gốc | Chuyển thể từ báo cáo TLCN `CLC_CNPM_1_LEDUCPHAT.pdf` |
| Cập nhật | 12/11/2026 |

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

> **Ranh giới SRS / SDD.** File này chỉ chứa *yêu cầu* — hệ thống phải làm gì
> (bối cảnh, mục tiêu, tác nhân, FR, NFR, use case, kịch bản kiểm thử). Mô hình dữ
> liệu, giao diện, công nghệ và thiết kế trợ lý AI — hệ thống được xây thế nào —
> nằm ở [`SDD.md`](SDD.md).
>
> Hai tài liệu được tách ngày 11/09/2026 (P-07, D-011), *trước* khi rà soát nội
> dung, để lịch sử Git của mỗi bên ghi lại trọn vẹn quá trình rà soát của riêng nó.
> Bảng đối chiếu số mục cũ → mới: [`PLAN.md`](PLAN.md) §6 dòng 4.

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
| FR-C-01 | Đăng nhập, đăng xuất, đổi mật khẩu, quên mật khẩu (link đặt lại gửi tới email đã đăng ký, dùng được một lần; email chưa đăng ký thì trang trả lời giống hệt), quản lý hồ sơ cá nhân (Avatar, Bio) |
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
| FR-A-02 | Kiểm soát sản phẩm do nhân viên đăng; xóa mềm hoặc vô hiệu hóa sản phẩm vi phạm |
| FR-A-03 | Quản lý danh mục: thêm, sửa, xóa danh mục hàng hóa dùng chung toàn hệ thống |
| FR-A-04 | Quản lý người dùng: tra cứu, phân quyền, khóa tài khoản vi phạm, xóa vĩnh viễn |
| FR-A-05 | Quản lý mã giảm giá: khởi tạo, thiết lập phần trăm giảm, phân phối tới khách hàng |
| FR-A-06 | Giám sát toàn hệ thống: truy xuất, kiểm tra toàn bộ đơn hàng của cửa hàng |

---

## 5. Yêu cầu phi chức năng

TLCN chỉ có bốn NFR mô tả định tính ("phản hồi nhanh", "chịu được lượng lớn truy
cập"). Ngày 05/11/2026 ba NFR được gắn một ngưỡng đo được và một cách đo lặp lại
được: hiệu năng, bảo mật, bảo trì (D-057, P-21). NFR-01 về giao diện bỏ cùng ngày:
câu "hiển thị đúng và ổn định trên mọi kích thước màn hình" không có ngưỡng đo được.
Mã NFR-02 → NFR-04 giữ nguyên vì `ISSUES.md` đã dẫn tới chúng. Ngưỡng là đề xuất, chốt cùng bản cam kết với GVHD
([`COMMITMENT.md`](COMMITMENT.md) §5.2).

| Mã | Nhóm | Yêu cầu và ngưỡng | Cách đo | Số đo 05/11/2026 |
|---|---|---|---|---|
| NFR-02 | **Hiệu năng** | Khi host đang chạy, 95% request tới mỗi trang chính trả về trong ≤ 3 giây. Tính thời gian máy chủ trả xong mã HTML của trang, không tính ảnh, CSS, JavaScript tải sau đó | Mỗi trang 20 request nối tiếp bằng `curl` từ máy ở TP.HCM, ghi thời gian tới khi nhận xong mã HTML, lấy mốc mà 95% request nhanh hơn. Năm trang: trang chủ, danh sách, chi tiết sản phẩm, tìm kiếm, danh mục | **Đạt** ở cả năm trang. Trang chậm nhất là trang chủ: 95% request xong trong 1,14 giây. Trang nhanh nhất là tìm kiếm: 0,53 giây. 100 request, không request nào lỗi |
| NFR-03 | **Bảo mật** | (a) Mật khẩu không lưu bản gốc mà lưu dạng băm PBKDF2-SHA256 với 1.000.000 vòng lặp; mật khẩu mới phải có ≥ 8 ký tự. (b) 100% request `http://` được chuyển sang `https://`. (c) Ở mỗi lần chạy CI: 0 secret lộ trong lịch sử Git, 0 thư viện có lỗ hổng đã biết | (a) Bộ băm mặc định của Django 5.2 và `AUTH_PASSWORD_VALIDATORS` trong `settings.py`. (b) `curl` tới địa chỉ `http://`. (c) Job `secret-scan` (gitleaks) và `dependency-audit` (pip-audit) của CI | **Đạt** cả ba. (b) Host trả 301 sang `https://`. (c) Lần CI gần nhất: gitleaks tìm ra 0 secret, pip-audit tìm ra 0 lỗ hổng |
| NFR-04 | **Bảo trì** | 0 lỗi lint, tỉ lệ dòng trùng lặp của mã Python ≤ 3%, độ phủ dòng lệnh của bộ test ≥ 70% | `ruff check`, `jscpd` và `pytest --cov` ở mỗi lần chạy CI. Lint và trùng lặp tính theo phạm vi ở [`COMMITMENT.md`](COMMITMENT.md) §5.1; độ phủ tính trên bốn app `core`, `userauths`, `useradmin`, `store_api`, không tính migration và test (`.coveragerc`) | **Đạt.** 0 lỗi lint, trùng lặp 0,66% số dòng, độ phủ 92% |

Hai điều không cam kết, có ghi lý do ở D-057. Thứ nhất, NFR-02 không tính lần đầu
sau khi host ngủ: gói miễn phí của Render tắt máy khi không có request trong 15 phút,
và request đánh thức nó mất khoảng 50 giây (đo được 48,7 giây ngày 05/11/2026). Thứ
hai, không có ngưỡng số người dùng đồng thời: host chạy một worker xử lý lần lượt
từng request, nên số này phụ thuộc gói host chứ không phụ thuộc mã nguồn (xem L-24
về các chỗ chưa an toàn khi tăng worker).

---

## 6. Danh sách Use Case

32 use case: 26 use case đặc tả trong TLCN (UC-01 → UC-26) và 6 use case thêm ở
KLTN (UC-27 → UC-32) cho các chức năng đã có trong mã nguồn mà đặc tả TLCN chưa có
(D-058, D-061). Bảng đặc tả đầy đủ của từng use case (Short Description, Actors,
Pre-/Post-Conditions, Main Flow, Alternate Flow, Exception Flow, Acceptance
Criteria) nằm ở báo cáo KLTN mục 3.2. Báo cáo không ghi mã UC, mà xếp use case theo
thứ tự chức năng cam kết. Acceptance criteria chép lại ở §6.2 và §6.3, mỗi tiêu chí
có mã AC-x.y để test dẫn tới.

| Mã | Use Case | Tác nhân |
|---|---|---|
| UC-01 | Đăng ký | A1 |
| UC-02 | Đăng nhập | A2, A3, A4 |
| UC-03 | Xem danh sách sản phẩm | A1, A2 |
| UC-04 | Xem chi tiết sản phẩm | A1, A2 |
| UC-05 | Tìm kiếm và lọc sản phẩm | A1, A2 |
| UC-06 | Quản lý giỏ hàng | A1, A2 |
| UC-07 | Đổi ngôn ngữ | A1, A2 |
| UC-08 | Gửi liên hệ | A1, A2 |
| UC-09 | Thanh toán và đặt hàng | A2 |
| UC-10 | Đăng xuất | A2, A3, A4 |
| UC-11 | Cập nhật hồ sơ cá nhân (xem, sửa, đổi mật khẩu) | A2 |
| UC-12 | Quản lý danh sách yêu thích | A2 |
| UC-13 | Xem lịch sử đơn hàng | A2 |
| UC-14 | Đánh giá sản phẩm | A2 |
| UC-15 | Tương tác với trợ lý AI | A1, A2 |
| UC-16 | Nhờ AI tìm sản phẩm | A1, A2 |
| UC-17 | Nhờ AI thêm vào giỏ | A1, A2 |
| UC-18 | Nhờ AI dẫn tới thanh toán | A1, A2 |
| UC-19 | Quản lý sản phẩm | A3, A4 |
| UC-20 | Quản lý đơn hàng | A3, A4 |
| UC-21 | Quản lý mã giảm giá | A4 |
| UC-22 | Quản lý người dùng | A4 |
| UC-23 | Quản lý danh mục | A4 |
| UC-24 | Quản lý toàn bộ sản phẩm (đổi trạng thái hiển thị, xóa mềm) | A4 |
| UC-25 | Quản lý toàn bộ đơn hàng | A4 |
| UC-26 | Xem báo cáo thống kê | A3, A4 |
| UC-27 | Khôi phục mật khẩu | A2 |
| UC-28 | Xem nhà cung cấp | A1, A2 |
| UC-29 | Xem danh sách đánh giá | A3, A4 |
| UC-30 | Cập nhật hồ sơ nhân viên | A3 |
| UC-31 | Quản lý nhà cung cấp | A4 |
| UC-32 | Xem hộp thư liên hệ | A4 |

### 6.1 Ràng buộc nghiệp vụ đáng chú ý

- **UC-06, UC-09:** số lượng của một dòng giỏ không vượt quá tồn kho. Máy chủ
  kiểm tra mỗi lần khách thêm vào giỏ, sửa số lượng và lúc tạo đơn; vượt thì hạ
  xuống đúng bằng tồn kho và báo cho khách biết đã hạ (D-024).
- **UC-06:** thêm một sản phẩm đã có trong giỏ thì số lượng được cộng vào số đang có,
  vẫn trong giới hạn tồn kho ở trên; đặt lại số lượng là việc của trang giỏ hàng. Nút
  thêm bị khóa trong lúc chờ máy chủ trả lời, nên bấm đúp chỉ tính một lần (L-18, D-044).
- **UC-06, UC-12:** giỏ hàng và wishlist chỉ đổi bằng POST có CSRF token. Link hay form
  đặt ở trang web khác không đổi được giỏ và wishlist của khách (L-19, D-043).
- **UC-06:** sản phẩm hết hàng khi đang nằm trong giỏ → dòng đó bị bỏ khỏi giỏ
  kèm thông báo, giống như sản phẩm bị gỡ bán.
- **UC-06, UC-09:** giá của mỗi dòng giỏ hàng và tổng tiền của đơn đều do hệ thống
  tra từ sản phẩm, không lấy theo con số trình duyệt gửi lên (D-022).
- **UC-06:** sản phẩm bị gỡ bán khi đang nằm trong giỏ của khách → dòng đó bị bỏ
  khỏi giỏ ở lần khách mở giỏ kế tiếp.
- **UC-09:** đơn chọn thanh toán online chỉ chuyển sang *đã thanh toán* khi VNPay
  xác nhận và chữ ký hợp lệ; trang hoàn tất chỉ hiển thị, không tự xác nhận (D-023).
- **UC-09:** đơn online chưa được VNPay xác nhận mà mở trang hoàn tất → quay về
  trang thanh toán kèm nhắc thanh toán, không hiện màn hình thanh toán thành công.
- **UC-09:** đơn chỉ thành *đã thanh toán* khi số tiền VNPay báo đúng bằng giá đơn
  lúc đó. Giá đơn đổi sau khi khách đã mở trang VNPay (thêm hàng ở tab khác, áp mã
  giảm giá) thì đơn giữ nguyên *chưa thanh toán*, khách về trang thanh toán thất bại
  kèm lời nhắc liên hệ cửa hàng, và vẫn trả lại được đúng giá đơn. Khoản đã trả
  nhân viên đối chiếu với VNPay và xử lý ngoài hệ thống (L-22, D-040). Mỗi lần lệch,
  ở trang quay về hay ở lời báo IPN, máy chủ ghi một dòng cảnh báo vào log kèm mã
  đơn và hai số tiền, để nhân viên tra được khi khách gọi tới (L-34).
- **UC-14:** chỉ đánh giá được sản phẩm đã nhận — khách có đơn chứa sản phẩm ấy ở
  trạng thái `Shipped` hoặc `Delivered` — và mỗi khách chỉ đánh giá một lần cho
  một sản phẩm. Chưa đủ điều kiện thì biểu mẫu không hiện, và máy chủ từ chối cả
  những yêu cầu gửi thẳng không qua biểu mẫu (D-027).
- **UC-14:** khách chỉ **tạo** đánh giá; sửa và xóa là việc của quản trị viên trong
  Django admin, theo nghĩa kiểm duyệt nội dung chứ không phải CRUD đầy đủ cho
  người viết (D-028).
- **UC-19, UC-24:** sản phẩm do nhân viên tạo hiển thị ngay ở trạng thái `published`
  — không có bước Admin duyệt, vì nhân viên là người của chính cửa hàng chứ không
  phải người bán bên ngoài (D-015, D-028). Admin vẫn ẩn hoặc gỡ bán được bất kỳ sản
  phẩm nào.
- **UC-08, UC-19:** nút gửi của form liên hệ và của form thêm, sửa sản phẩm bị khóa khi
  form đã gửi đi, nên bấm đúp chỉ gửi một lần. Chặn ở trình duyệt, không chặn được
  request do script gửi trùng (L-21, L-23, D-044).
- **UC-19:** sản phẩm phải có danh mục và nhà cung cấp. Nhân viên để trống một trong
  hai ở form thêm hoặc sửa thì máy chủ từ chối và báo ô còn thiếu; hệ thống không tự
  chọn hộ (L-27, D-039).
- **Mọi form:** dữ liệu sai thì máy chủ từ chối, không lưu gì, và trang hiện câu lỗi ngay
  dưới ô nhập sai, chữ đỏ, cùng ngôn ngữ với trang. Ô đã gõ giữ nguyên, trừ ô mật khẩu.
  Không chuỗi nào dài hơn cột của database được gửi xuống database (L-46, L-48, L-50,
  D-054, D-055).
- **UC-02:** đăng nhập không được, vì sai mật khẩu, email chưa đăng ký hay để trống, đều
  ra một câu chung "Email hoặc mật khẩu không đúng", không in lại email vừa gõ; ô email
  giữ chữ đã gõ (L-52).
- **UC-08:** form liên hệ bắt buộc họ tên, email đúng định dạng và nội dung; số điện thoại
  và tiêu đề không bắt buộc (L-50).
- **UC-09:** thông tin giao hàng bắt buộc họ tên, email đúng định dạng và địa chỉ; địa chỉ
  dài tới 255 ký tự (L-50, D-055).
- **UC-14:** gửi đánh giá xong khách vẫn ở trang sản phẩm và thấy câu báo; đánh giá bị
  từ chối thì câu lỗi hiện ngay trên trang (L-49).
- **UC-19:** giá bán, giá cũ và số lượng trong kho không được âm (L-53).
- **UC-19:** trang thêm và trang sửa sản phẩm có ô khối lượng hoặc thể tích, thành phần và
  cách bảo quản. Để trống ô khối lượng thì sản phẩm không có khối lượng, không bị gán "1 kg";
  trợ lý AI đọc khối lượng từ đây khi báo giá (L-71).
- **Đổi mật khẩu nhân viên (CN-32):** cùng quy tắc với trang của khách: ô che chữ, mật
  khẩu mới phải qua bộ kiểm mật khẩu của Django, đổi xong vẫn đăng nhập (L-51).
- **UC-03, UC-19:** sản phẩm còn sót lại không có danh mục hay nhà cung cấp vẫn bán
  bình thường, thẻ sản phẩm chỉ bỏ link tương ứng. Một dòng dữ liệu thiếu không được
  làm hỏng trang của các sản phẩm khác (L-27, D-039).
- **UC-19, UC-24:** xóa sản phẩm là xóa mềm: dòng dữ liệu, ảnh và đánh giá còn nguyên,
  quản trị viên khôi phục được trong Django admin. Nhân viên phải xác nhận trước khi
  xóa. Máy chủ chỉ nhận thao tác xóa gửi từ form của trang quản lý, nên mở một đường
  link không xóa được gì (L-28, L-29, D-041).
- **UC-03, UC-19:** sản phẩm đã xóa không còn hiện ở bất kỳ trang nào của khách, kể cả
  wishlist. Trang của sản phẩm, danh mục hay nhà cung cấp đã xóa trả 404, không trả lỗi
  máy chủ; khách bấm yêu thích sản phẩm vừa bị xóa thì được báo sản phẩm không còn bán
  (L-28, D-041).
- **FR-A-02:** xóa mềm một nhà cung cấp thì sản phẩm của họ ẩn theo, dù xóa từng nhà
  cung cấp hay chọn nhiều rồi xóa hàng loạt trong Django admin (L-36, D-041).
- **UC-20:** **không có thao tác xóa đơn hàng** — lịch sử giao dịch phải được giữ
  lại; đơn đã `Delivered` hoặc `Cancelled` không đổi được trạng thái. Máy chủ chỉ
  nhận đúng bốn trạng thái `Processing`, `Shipped`, `Delivered`, `Cancelled`; giá
  trị khác bị từ chối và đơn giữ nguyên trạng thái cũ (D-026, D-033).
- **UC-20:** đơn chỉ đi tới, mỗi lần một bước: `Processing` sang `Shipped`, rồi
  `Shipped` sang `Delivered`. Lùi lại, nhảy thẳng từ `Processing` sang `Delivered`,
  hay gửi lại đúng trạng thái đơn đang có đều bị máy chủ từ chối và đơn giữ nguyên
  trạng thái cũ. Tồn kho bị trừ đúng một lần, lúc đơn sang `Shipped`. Hàng đã rời
  kho mà có sự cố (giao hụt, khách trả lại) thì nhân viên chỉnh tồn kho ở trang
  sản phẩm, không lùi trạng thái đơn (D-032).
- **UC-20:** khách gọi điện báo hủy thì nhân viên chuyển đơn sang `Cancelled`. Hủy
  được đơn đang `Processing` hoặc `Shipped`, không hủy được đơn đã `Delivered`;
  khách không tự hủy trên web. Hủy đơn không cộng lại tồn kho: đơn đã `Shipped` mà
  hàng về được kho thì nhân viên cộng tay ở trang sản phẩm. Đơn đã thanh toán qua
  VNPay bị hủy vẫn ghi là đã thanh toán, tiền hoàn cho khách ngoài hệ thống (D-033).
- **UC-09, UC-20:** đơn đã `Cancelled` thì khách không thanh toán hay đặt lại được
  nữa: trang thanh toán, nút COD và lối sang VNPay đều đưa khách về trang tài khoản
  kèm thông báo đơn đã hủy. Khách đặt hàng lần sau thì hệ thống tạo đơn mới, không
  ghi vào đơn đã hủy (D-033).
- **UC-09, UC-20:** các bước thanh toán của khách chỉ ghi phương thức thanh toán,
  không đổi trạng thái giao hàng của đơn. Đơn đã `Shipped` mà khách bấm đặt COD
  lần nữa thì vẫn là `Shipped` (L-12, D-033).
- **UC-13, UC-20:** trạng thái đơn hiện theo ngôn ngữ đang chọn, không in giá trị
  lưu trong database: `processing` là Đang xử lý / Processing, `shipped` là Đang
  giao hàng / Shipping, `delivered` là Đã giao / Delivered, `cancelled` là Đã hủy /
  Cancelled (D-033).
- **UC-13:** khách chỉ mở được chi tiết đơn của chính mình. URL gọi đơn bằng mã đơn
  (`oid`), không bằng số thứ tự; đơn không có hoặc của khách khác thì trang trả 404
  (L-32, D-047). Lịch sử đơn không kèm chức năng đặt địa chỉ mặc định (L-33, D-047).
- **UC-20:** trang nhân viên cũng gọi đơn bằng `oid`, ở cả trang chi tiết đơn lẫn
  trang đổi trạng thái; mã đơn không có thì trang trả 404 (L-39, L-44, D-047).
- **UC-07:** link trên trang giữ ngôn ngữ đang xem, kể cả link sản phẩm trong giỏ
  mini dựng bằng JavaScript; khách vào thẳng trang `/en/` bấm sang sản phẩm vẫn ở
  trang tiếng Anh (L-35).
- **Mọi UC có giao diện:** một trang chỉ dùng một ngôn ngữ. Trang `/vi/` không còn
  chữ tiếng Anh, trang `/en/` không còn chữ tiếng Việt, kể cả thông báo sau khi bấm
  nút, câu lỗi của form (cả câu lỗi do Django viết), câu JavaScript hiện ra và câu
  trả lời JSON mà trang in ra. Tên riêng và dữ liệu (tên sản phẩm, nhà cung cấp,
  khách) giữ nguyên như đã nhập (L-47, L-55 → L-57, D-056).
- **Mọi UC có giao diện:** trang chỉ hiện nội dung thật của Grocerly, không còn nội
  dung mẫu của theme (cửa hàng, người, sản phẩm, số điện thoại giả, Lorem ipsum).
  Không có form nào gửi về `#`. Trang chính sách bảo mật, điều khoản, hướng dẫn mua
  hàng và giới thiệu chỉ mô tả những gì hệ thống làm thật. Cửa hàng chưa có địa chỉ
  riêng nên chân trang và trang liên hệ ghi địa chỉ của trường và email của sinh viên
  (L-58, D-056).
- **UC-03, UC-04, UC-24:** chỉ sản phẩm ở trạng thái `published` có trang chi tiết và có mặt
  ở các trang của khách. Sản phẩm nháp, đã tắt, chờ duyệt hay bị từ chối thì trang của nó trả
  404 như sản phẩm đã xóa, không hiện ở tab danh mục của trang chủ, và không được tính vào số
  sản phẩm in cạnh mỗi danh mục, nhà cung cấp (L-66).
- **UC-23:** xóa mềm một danh mục không xóa sản phẩm của nó: sản phẩm vẫn bán, thẻ sản phẩm
  chỉ bỏ link tới danh mục đã xóa, trang của danh mục trả 404. Trang quản trị không cảnh báo
  riêng khi xóa danh mục còn sản phẩm (L-67, D-041). Câu "cảnh báo sản phẩm bị mồ côi" của
  TLCN đã bỏ.
- **UC-21:** mã giảm giá gồm mã, phần trăm giảm và cờ bật/tắt; không có hạn dùng, không đếm
  lượt dùng, không chặn hai mã trùng chữ. Phần trăm giảm từ 1 tới 100; trang quản trị từ chối
  số ngoài khoảng này. Mã đã tắt hay đã xóa mềm thì khách nhập vào bị báo không tồn tại; mỗi
  mã áp một lần cho một đơn (L-68, D-059).
- **UC-22:** tài khoản nhân viên được tạo bằng cách: người đó tự đăng ký như khách, quản trị
  viên bật quyền nhân viên (`is_staff`) trong trang quản trị. Khóa tài khoản là bỏ cờ "đang
  hoạt động". Không có gửi email hàng loạt (L-70, D-059).
- **UC-25:** Admin không được xóa vĩnh viễn đơn hàng, để phục vụ đối soát kế toán.
  Trong Django admin, cả đơn lẫn dòng đơn đều không có nút xóa hay lệnh xóa hàng
  loạt, và yêu cầu xóa gửi thẳng bị từ chối (L-40). Trang đơn và dòng đơn trong Django admin
  chỉ đọc: không thêm, không sửa; trạng thái giao hàng và thanh toán chỉ đổi qua trang nhân
  viên, nơi có các ràng buộc của UC-20 (L-69).
- **UC-26:** doanh thu, doanh thu theo tháng và số sản phẩm đã bán chỉ tính đơn đã
  thanh toán và không bị hủy. Đơn VNPay đã trả tiền rồi bị hủy vẫn nằm trong danh
  sách đơn nhưng không còn được cộng vào doanh thu (D-033).
- **UC-16, UC-17:** trợ lý AI và API công khai `/api/v1/products/` chỉ thấy đúng
  những sản phẩm mà khách thấy ở cửa hàng — sản phẩm chưa duyệt hoặc đã bị gỡ bán
  thì AI không tìm ra và cũng không đề xuất thêm vào giỏ (D-025).
- **UC-17:** AI chỉ thêm vào giỏ khi sản phẩm còn hàng; hết hàng → AI từ chối và
  nói rõ là hết hàng, thay vì im lặng hoặc đề nghị thêm.
- **UC-17:** AI chỉ đề nghị số lượng từ 1 tới số còn trong kho; khách hỏi nhiều hơn
  thì AI nói kho còn bao nhiêu. Câu báo sau khi khách bấm xác nhận nói đúng số lượng
  giỏ hàng đang giữ, không lặp lại số AI đã đề nghị (L-14, D-035).
- **UC-17:** số AI đề nghị được tính thêm vào số đã có trong giỏ, nên tổng sau khi thêm
  không vượt tồn kho. Mỗi lần AI đề nghị chỉ xác nhận được một lần (L-18, D-044).
- **UC-16, UC-17:** khách nhờ "tìm rồi thêm vào giỏ" trong cùng một câu thì AI tìm,
  rồi hỏi xác nhận thêm vào giỏ như khi khách bảo thêm, không báo lỗi kết nối. Cùng
  một câu, AI dùng được nhiều công cụ nối nhau, tối đa ba lần; cần nhiều hơn thì AI
  nhờ khách nói lần lượt từng bước, cũng không báo lỗi kết nối (L-30).
- **UC-16:** tên sản phẩm trong cửa hàng viết bằng tiếng Việt. Khách hỏi trợ lý bằng
  tiếng Anh thì AI dịch tên hàng sang tiếng Việt rồi mới tìm, nên hỏi "watermelon" vẫn
  ra dưa hấu (L-31). Ô tìm kiếm thường của cửa hàng không dịch: ở trang `/en/` vẫn
  phải gõ tên tiếng Việt.
- **UC-16:** AI tìm bằng chữ chính của tên hàng, không thêm chữ chung như "thịt",
  "rau", "trái", vì cửa hàng chỉ ra sản phẩm có đủ mọi chữ của câu tìm. Hỏi "có bán
  bò không" thì AI tìm "bò" và ra "Đùi bò 150g" (L-42, D-049).
- **UC-17:** khách sửa số lượng ngay sau câu hỏi xác nhận ("chỉ lấy 10 thôi") thì AI
  vẫn biết đó là sản phẩm nào: kết quả tìm của tin nhắn trước đi kèm câu hỏi xác
  nhận, như với danh sách chọn ở AC-17.3 (L-38).
- **UC-15:** chữ cố định của khung chat (lời chào, nút bấm, câu hỏi xác nhận, câu
  báo lỗi) hiện theo ngôn ngữ của trang đang mở, như mọi chữ khác trên trang. Lời AI
  tự sinh không thuộc ràng buộc này (L-15, D-035).
- **UC-15:** một model Gemini quá tải, hết quota hay không trả lời trong 8 giây thì
  trợ lý chuyển sang model kế tiếp trong danh sách bốn model, khách vẫn nhận câu trả
  lời. Cả bốn đều hỏng, hoặc tin nhắn đã tốn 25 giây, thì khung chat nhận câu báo
  trục trặc kết nối (hay câu báo hết quota) chứ không nhận lỗi máy chủ, và khách gửi
  lại được (L-37, D-051, D-060).
- **UC-18:** giỏ trống, kể cả giỏ vừa bị xóa hết hàng, thì AI nhắc thêm hàng chứ
  không đưa nút thanh toán (L-41).

Các ràng buộc trên là ghi chép theo từng lần sửa lỗi. Tiêu chí kiểm chứng được
của từng use case ở §6.2 (UC-17) và §6.3 (31 use case còn lại).

### 6.2 Acceptance criteria của UC-17 Nhờ AI thêm vào giỏ

GVHD yêu cầu có cơ chế kiểm soát việc AI đặt hàng: đúng sản phẩm, số lượng hợp lý,
khách thấy rõ mình sắp trả bao nhiêu (nhận xét báo cáo Tuần 7, P-42). Các ràng buộc ở
§6.1 vẫn giữ nguyên. Mọi tiêu chí dưới đây do máy chủ kiểm, không dựa vào lời dặn
Gemini, nên test tự động kiểm được bằng Gemini giả lập (D-048).

- **AC-17.1 Giá trong câu xác nhận.** Khi AI đề nghị thêm một sản phẩm, câu hỏi xác
  nhận ghi số lượng, tên sản phẩm, đơn giá và thành tiền (đơn giá nhân số lượng). Giá
  lấy từ database lúc hỏi và viết như ở các trang khác của cửa hàng (`25.000 ₫`),
  không lấy con số AI nói ra. Giỏ vẫn tự tính lại giá lúc thêm (§6.1).
- **AC-17.2 Số lượng lớn hơn thường lệ.** Một lần thêm từ 11 đơn vị trở lên thì câu
  xác nhận mở đầu bằng lời hỏi lại, nói số lượng này lớn hơn thường lệ và nhờ khách
  kiểm tra, còn nút xác nhận ghi đúng con số đó (`Đúng 30, thêm vào giỏ`). Từ 10 trở
  xuống thì hỏi như thường. Ngưỡng này không thay giới hạn tồn kho: vượt kho vẫn bị
  từ chối như trước.
- **AC-17.3 Nhiều sản phẩm cùng khớp.** Trong cùng một tin nhắn của khách, AI tìm
  sản phẩm rồi đề nghị thêm vào giỏ, mà lần tìm gần nhất ra từ hai sản phẩm trở lên
  thêm được đúng số lượng đó, thì hệ thống không đề nghị sản phẩm AI tự chọn. Thay vào
  đó, khung chat hiện tất cả các sản phẩm ấy (tối đa 5, theo thứ tự tìm được), mỗi sản
  phẩm một nút ghi số lượng, tên và thành tiền. Bấm một nút là vừa chọn vừa xác nhận;
  sau đó mọi nút của lần hỏi ấy tắt, nên chỉ một sản phẩm được thêm. Khách vẫn có thể
  gõ chữ thay vì bấm.
- **AC-17.4 Khách đã chọn rồi thì không hỏi lại.** Tin nhắn của khách không kèm lần
  tìm nào (ví dụ "thêm cái thứ hai" sau khi đã xem danh sách), hoặc lần tìm chỉ ra một
  sản phẩm thêm được, thì AI hỏi xác nhận đúng sản phẩm đó như AC-17.1.
- **AC-17.5 Kết quả đọc được bằng máy.** Câu trả lời của `/api/v1/chat/` ghi đề nghị
  dưới dạng dữ liệu, không chỉ bằng câu chữ: `action` là `confirm_add_cart` (kèm
  `product`) hoặc `choose_product` (kèm `choices`), mỗi đề nghị có `pid`, `qty`,
  `price`, `total` và cờ `large_qty`. Bộ kịch bản đánh giá AI (P-42 phần d) so các
  trường này với đáp án.

Bốn tiêu chí dưới đây đúng từ trước P-42 (L-13 → L-17). Bảng use case của báo cáo
KLTN mục 3.2 có cả chín tiêu chí, viết bằng lời không kèm mã.

- **AC-17.6** Không có lời gọi hàm nào từ Gemini tự làm thay đổi giỏ hàng. Giỏ chỉ đổi sau khi khách bấm xác nhận.
- **AC-17.7** Trợ lý chỉ đề nghị số lượng từ 1 tới tồn kho hiện tại.
- **AC-17.8** Câu báo sau khi xác nhận nói đúng số lượng giỏ đang giữ, không lặp lại số đã đề nghị.
- **AC-17.9** Nút xác nhận hoạt động đúng với mọi tên sản phẩm, kể cả tên có dấu nháy.

### 6.3 Acceptance criteria của các use case còn lại

Chép nguyên văn từ dòng Acceptance Criteria trong bảng use case của báo cáo KLTN mục
3.2 (12/11/2026). Mã AC-x.y: x là số UC, y là thứ tự tiêu chí trong bảng. Sửa tiêu
chí ở bên nào thì sửa bên kia trong cùng lượt (D-061).

**UC-01 Đăng ký**

- **AC-1.1** Đăng ký với dữ liệu hợp lệ tạo đúng một tài khoản và một hồ sơ, người dùng ở trạng thái đăng nhập ngay sau đó.
- **AC-1.2** Đăng ký với email đã tồn tại không tạo thêm tài khoản nào.
- **AC-1.3** Mật khẩu được lưu ở dạng băm, không bao giờ ở dạng gốc.

**UC-02 Đăng nhập**

- **AC-2.1** Email và mật khẩu đúng thì đăng nhập được và được chuyển đúng trang theo vai trò.
- **AC-2.2** Mật khẩu sai thì không có phiên làm việc nào được tạo.
- **AC-2.3** Tài khoản bị khóa không đăng nhập được dù mật khẩu đúng.
- **AC-2.4** Email chưa đăng ký và mật khẩu sai nhận cùng một câu báo, nên người ngoài không dò được email nào đã đăng ký.

**UC-03 Xem danh sách sản phẩm**

- **AC-3.1** Sản phẩm ở trạng thái khác "đang bán", hoặc đã bị xóa mềm, không xuất hiện ở bất kỳ danh sách nào của khách.
- **AC-3.2** Một sản phẩm thiếu danh mục hay nhà cung cấp vẫn hiện bình thường, chỉ không có liên kết tương ứng. Trang không bị lỗi máy chủ vì một dòng dữ liệu thiếu.
- **AC-3.3** Số sản phẩm in cạnh mỗi danh mục và nhà cung cấp chỉ đếm sản phẩm đang bán.

**UC-04 Xem chi tiết sản phẩm**

- **AC-4.1** Mở trang của sản phẩm đã xóa hoặc không ở trạng thái đang bán trả 404, không trả lỗi máy chủ.
- **AC-4.2** Điểm trung bình và tỉ lệ các mức sao tính từ đúng các đánh giá của sản phẩm đó.

**UC-05 Tìm kiếm và lọc sản phẩm**

- **AC-5.1** Kết quả tìm kiếm và kết quả lọc chỉ chứa sản phẩm đang bán.
- **AC-5.2** Lọc theo nhiều danh mục trả về hợp các danh mục đó. Kết hợp danh mục với khoảng giá trả về giao của hai điều kiện.

**UC-06 Quản lý giỏ hàng**

- **AC-6.1** Tổng tiền của giỏ bằng tổng (giá trong cơ sở dữ liệu nhân số lượng) của các dòng, dù trình duyệt gửi lên bất kỳ giá nào.
- **AC-6.2** Không dòng giỏ nào có số lượng lớn hơn tồn kho sau khi máy chủ xử lý.
- **AC-6.3** Sản phẩm hết hàng không nằm lại trong giỏ.
- **AC-6.4** Thêm một sản phẩm đã có trong giỏ thì số lượng được cộng thêm, không bị ghi đè.
- **AC-6.5** Giỏ chỉ đổi bằng yêu cầu POST có mã CSRF. Một đường link hay biểu mẫu đặt ở trang web khác không đổi được giỏ của khách.

**UC-07 Đổi ngôn ngữ**

- **AC-7.1** Sau khi chọn tiếng Anh, các trang kế tiếp đều ở /en/ cho tới khi người dùng đổi lại.
- **AC-7.2** Chữ cố định của khung chat (lời chào, nút xác nhận, câu báo lỗi) theo đúng ngôn ngữ của trang. Lời do AI tự sinh không thuộc tiêu chí này.

**UC-08 Gửi liên hệ**

- **AC-8.1** Một lần gửi hợp lệ tạo đúng một tin nhắn trong hộp thư liên hệ.
- **AC-8.2** Gửi thiếu ô bắt buộc không tạo tin nhắn nào.
- **AC-8.3** Bấm Gửi hai lần liền chỉ tạo một tin nhắn.

**UC-09 Thanh toán và đặt hàng**

- **AC-9.1** Giá đơn được máy chủ tính từ giá trong cơ sở dữ liệu. Sửa giá trong yêu cầu gửi lên không làm đổi giá đơn.
- **AC-9.2** Đơn VNPay chỉ thành "đã thanh toán" khi chữ ký hợp lệ, mã kết quả là thành công, và số tiền bằng đúng giá đơn.
- **AC-9.3** Các bước thanh toán của khách chỉ ghi phương thức thanh toán, không đổi trạng thái giao hàng của đơn.
- **AC-9.4** Đặt hàng lần sau khi đơn trước đã bị hủy thì tạo đơn mới, không ghi vào đơn đã hủy.

**UC-10 Đăng xuất**

- **AC-10.1** Sau khi đăng xuất, mở một trang cần đăng nhập thì bị chuyển về trang Đăng nhập.

**UC-11 Cập nhật hồ sơ cá nhân**

- **AC-11.1** Sau khi đổi mật khẩu, mật khẩu cũ không còn đăng nhập được.
- **AC-11.2** Khách chỉ sửa được hồ sơ của chính mình.

**UC-12 Quản lý danh sách yêu thích**

- **AC-12.1** Sản phẩm đã bị xóa không hiện trong danh sách yêu thích và không được tính vào số đếm.
- **AC-12.2** Danh sách yêu thích chỉ đổi bằng yêu cầu POST có mã CSRF.

**UC-13 Xem lịch sử đơn hàng**

- **AC-13.1** Khách chỉ thấy đơn của chính mình. Mở chi tiết đơn của người khác, hoặc mã đơn không tồn tại, thì trang trả 404.
- **AC-13.2** Biểu đồ số đơn theo tháng ở trang tài khoản chỉ đếm đơn của chính khách.

**UC-14 Đánh giá sản phẩm**

- **AC-14.1** Chỉ khách có đơn chứa sản phẩm ở trạng thái đang giao hoặc đã giao mới tạo được đánh giá.
- **AC-14.2** Mỗi khách có tối đa một đánh giá cho một sản phẩm.
- **AC-14.3** Khách chỉ tạo đánh giá. Sửa và xóa đánh giá là việc kiểm duyệt của quản trị viên.

**UC-15 Tương tác với trợ lý AI**

- **AC-15.1** Mỗi tin nhắn của khách chỉ nằm một lần trong lịch sử hội thoại gửi Gemini.
- **AC-15.2** Chữ cố định của khung chat theo ngôn ngữ của trang đang mở.
- **AC-15.3** Mọi nội dung hiện trong khung chat (lời AI, tên sản phẩm, chữ khách gõ) đều được hiển thị như chữ thường. Một tên sản phẩm chứa thẻ HTML không thể chạy mã trên trình duyệt của khách.

**UC-16 Nhờ AI tìm sản phẩm**

- **AC-16.1** Trợ lý không bao giờ đưa ra sản phẩm đã bị gỡ bán, đã bị xóa, hoặc đã hết hàng.
- **AC-16.2** API công khai /api/v1/products/ dùng đúng điều kiện lọc như trang cửa hàng.

**UC-18 Nhờ AI dẫn tới thanh toán**

- **AC-18.1** Trợ lý không tự tạo đơn hay tự thanh toán. Mọi bước sau đó do khách thao tác trên các trang thanh toán thường.
- **AC-18.2** Giỏ trống thì khung chat không hiện nút đi tới thanh toán.

**UC-19 Quản lý sản phẩm**

- **AC-19.1** Thao tác xóa chỉ được nhận từ biểu mẫu POST của trang quản lý. Mở một đường link không xóa được gì.
- **AC-19.2** Sản phẩm đã xóa không còn hiện ở bất kỳ trang nào của khách, nhưng vẫn khôi phục được trong trang quản trị.
- **AC-19.3** Sản phẩm mới tạo không có danh mục hay nhà cung cấp thì không lưu được.
- **AC-19.4** Khách hàng và người chưa đăng nhập không vào được trang quản lý sản phẩm.
- **AC-19.5** Bấm Tạo hai lần liền chỉ tạo một sản phẩm.
- **AC-19.6** Ô sửa tồn kho ngay trên dòng gửi kèm mã CSRF. Yêu cầu không có mã bị từ chối.

**UC-20 Quản lý đơn hàng**

- **AC-20.1** Không có thao tác xóa đơn hàng.
- **AC-20.2** Tồn kho bị trừ đúng một lần cho mỗi đơn, lúc đơn sang đang giao.
- **AC-20.3** Đơn đã giao không hủy được.
- **AC-20.4** Khách không tự hủy đơn trên web.
- **AC-20.5** Kho trừ theo đúng sản phẩm của từng dòng đơn, kể cả khi sản phẩm đã đổi tên sau khi khách đặt.

**UC-21 Quản lý mã giảm giá**

- **AC-21.1** Mã đã tắt hoặc đã xóa mềm thì khách nhập vào sẽ bị báo không tồn tại.
- **AC-21.2** Mỗi mã chỉ áp một lần cho một đơn.
- **AC-21.3** Không lưu được mã có phần trăm giảm ngoài khoảng 1 - 100, nên không đơn nào bị giảm tới giá âm.

**UC-22 Quản lý người dùng**

- **AC-22.1** Tài khoản bị bỏ đánh dấu hoạt động không đăng nhập được.
- **AC-22.2** Tài khoản được bật quyền nhân viên thì sau khi đăng nhập vào được trang quản lý cửa hàng.

**UC-23 Quản lý danh mục**

- **AC-23.1** Danh mục đã xóa không hiện ở cửa hàng nhưng vẫn khôi phục được.
- **AC-23.2** Xóa một danh mục không làm sập trang của bất kỳ sản phẩm nào.
- **AC-23.3** Sau khi xóa một danh mục, không trang nào của khách còn link tới danh mục đó.

**UC-24 Quản lý toàn bộ sản phẩm**

- **AC-24.1** Sản phẩm chuyển khỏi trạng thái đang bán thì biến mất khỏi cửa hàng, kết quả tìm kiếm, trợ lý AI và API, và trang chi tiết của nó trả 404.
- **AC-24.2** Không có màn hình nào xóa hẳn sản phẩm. Mọi thao tác xóa đều là xóa mềm.
- **AC-24.3** Khôi phục một nhà cung cấp đã xóa thì các sản phẩm bị xóa cùng lúc với nhà cung cấp đó cũng trở lại.

**UC-25 Quản lý toàn bộ đơn hàng**

- **AC-25.1** Đơn hàng không bị xóa vĩnh viễn, để phục vụ đối soát kế toán. Trang quản trị không có nút xóa đơn hay dòng đơn, và yêu cầu xóa gửi thẳng bị từ chối.
- **AC-25.2** Quản trị viên không thêm đơn bằng tay, không sửa được trạng thái giao hàng, trạng thái thanh toán hay giá của đơn trong trang quản trị.

**UC-26 Xem báo cáo thống kê**

- **AC-26.1** Doanh thu, doanh thu theo tháng và số sản phẩm đã bán chỉ tính đơn đã thanh toán và không bị hủy.
- **AC-26.2** Đơn VNPay đã trả tiền rồi bị hủy vẫn nằm trong danh sách đơn nhưng không được cộng vào doanh thu.
- **AC-26.3** Khách hàng và người chưa đăng nhập không mở được bảng điều khiển.

**UC-27 Khôi phục mật khẩu**

- **AC-27.1** Liên kết đặt lại chỉ dùng được một lần. Sau khi đổi mật khẩu, mở lại liên kết cũ thì bị báo không hợp lệ.
- **AC-27.2** Sau khi đặt lại, mật khẩu cũ không còn đăng nhập được, mật khẩu mới thì được.

**UC-28 Xem nhà cung cấp**

- **AC-28.1** Nhà cung cấp đã xóa không có trong danh sách. Mở đường dẫn cũ của họ trả 404.

**UC-29 Xem danh sách đánh giá**

- **AC-29.1** Trang chỉ đọc. Nhân viên không sửa hay xóa được đánh giá ở đây; việc kiểm duyệt thuộc quản trị viên, làm trong trang quản trị.

**UC-30 Cập nhật hồ sơ nhân viên**

- **AC-30.1** Sau khi đổi, mật khẩu cũ không còn đăng nhập được.
- **AC-30.2** Đổi mật khẩu xong, nhân viên vẫn ở trong trang quản lý, không bị đăng xuất.

**UC-31 Quản lý nhà cung cấp**

- **AC-31.1** Xóa rồi khôi phục một nhà cung cấp đưa đúng các sản phẩm bị ẩn theo nó trở lại.
- **AC-31.2** Bấm xóa lần nữa trên một nhà cung cấp đã xóa không làm hỏng khả năng khôi phục.
- **AC-31.3** Chọn nhiều nhà cung cấp rồi xóa hàng loạt cũng ẩn hàng của từng nhà cung cấp, như xóa từng cái.

**UC-32 Xem hộp thư liên hệ**

- **AC-32.1** Mọi tin nhắn gửi thành công ở trang Liên hệ đều có trong hộp thư.
---

## 7. Kiểm thử

Phương pháp: kiểm thử hộp đen (Black-box), dựa trên yêu cầu chức năng và giao diện.

| Mã | Kịch bản | Kết quả mong đợi | Trạng thái |
|---|---|---|---|
| TC_01 | Đăng nhập email + mật khẩu đúng | Đăng nhập thành công, chuyển về trang chủ | PASS |
| TC_02 | Đăng nhập sai mật khẩu | Báo lỗi "Email hoặc mật khẩu không chính xác" | PASS |
| TC_03 | Đăng ký với thông tin hợp lệ | Tạo tài khoản, chuyển về trang chủ đã đăng nhập | PASS |
| TC_04 | Đăng ký trùng email | Báo lỗi "Email này đã được sử dụng" | PASS |
| TC_05 | Thêm giỏ → điền địa chỉ → đặt hàng (COD) | Đơn lưu vào CSDL, chuyển trang thành công, giỏ được làm sạch | PASS |

> ⚠️ **Ghi chú cho KLTN:** 5 test case trên là kiểm thử **thủ công** của TLCN. Từ
> 16/09/2026 cả 5 đã có test tự động tương ứng (P-12, D-018): TC_01 → TC_04 ở
> `grocerly/userauths/tests/test_auth.py`, TC_05 ở
> `grocerly/core/tests/test_checkout.py` (mỗi test ghi chú `# TC_0x`).
>
> Test tự động chỉ kiểm **hành vi** (đăng nhập được hay không, có tạo tài khoản hay
> không), không kiểm câu chữ thông báo, vì cột *Kết quả mong đợi* của TC_02 và TC_04
> không khớp mã nguồn: lúc viết test, sai mật khẩu thì code báo `User does not
> exist. Please try again.` (tiếng Anh, không qua `gettext`); trùng email thì là
> thông báo mặc định của Django cho trường `email` duy nhất. Từ L-52 (05/11/2026),
> email chưa đăng ký và mật khẩu sai cùng nhận câu "Email hoặc mật khẩu không
> đúng."; acceptance criteria của UC-02 (AC-2.4, §6.3) chốt điều đó là *cùng một
> câu*, không chốt câu chữ. Danh sách test và độ phủ: [`PLAN.md`](PLAN.md) P-12, P-13.

---

## 8. Hạn chế đã ghi nhận

Trích nguyên trạng từ phần Kết luận của TLCN:

1. Biểu đồ thống kê cho người bán và quản trị viên còn đơn giản, chưa đa dạng
   chiều phân tích dữ liệu.
2. Tìm kiếm mới ở mức theo tên và lọc theo danh mục cơ bản; chưa có full-text
   search hay gợi ý thông minh.
3. Chưa có tương tác thời gian thực (live chat giữa khách hàng và người bán).
4. Hệ gợi ý sản phẩm dựa trên tiêu chí tĩnh (nổi bật, ngẫu nhiên), chưa học theo
   hành vi người dùng.

Ghi nhận thêm ở KLTN, khi đối chiếu đặc tả với mã nguồn (D-059):

5. Mã giảm giá không có hạn dùng, không giới hạn số lượt dùng và không chặn hai mã
   trùng chữ (L-68).
6. Quản lý người dùng dùng trang mặc định của Django admin: ô mật khẩu là chuỗi đã
   băm, nên quản trị viên không đặt mật khẩu hộ nhân viên; quản trị viên tự bỏ quyền
   hay tự khóa được chính mình, và xóa hẳn được một tài khoản (L-70).

---

## 9. Lịch sử chỉnh sửa đặc tả

Nhật ký các lần sửa file này (và [`SDD.md`](SDD.md)) được ghi tập trung tại
[`PLAN.md`](PLAN.md) §6, để việc chỉnh đặc tả nằm cùng chỗ với việc theo dõi tiến
độ thay vì tách làm hai nơi.

Khi sửa bất kỳ mục nào ở trên, thêm một dòng vào bảng đó: sửa gì, vì sao, và commit
tương ứng.
