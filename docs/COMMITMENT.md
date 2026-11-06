# BẢN CAM KẾT SẢN PHẨM — Grocerly (KLTN)

> **⚠️ BẢN NHÁP — chưa ký.** Soạn ngày 10/09/2026 để trao đổi với GVHD. Phần
> chức năng (§2) đã đối chiếu với mã nguồn; phần metric và KPI (§5) mới có mục
> chất lượng mã nguồn (§5.1, soạn ngày 24/09/2026).

| | |
|---|---|
| Đề tài | Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng |
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| Hạn chốt | **22/11/2026** — hết Tuần 10 (rubric Mục 2 Bước 3: từ Tuần 7 đến Tuần 10; gate G1). Mục nộp trên portal hạn 16:49 Thứ Hai 23/11/2026, cần GVHD xác nhận |
| Theo dõi | [`PLAN.md`](PLAN.md) P-03 |

**Vì sao văn bản này quan trọng.** Rubric TC2.2 chấm theo *"tỉ lệ chức năng đã cam
kết ở Bước 3 hoạt động"* — danh sách ở §2 chính là mẫu số. Cam kết quá nhiều thì
tự hạ điểm TC2.2; cam kết quá ít thì dính gate G9 (sản phẩm không tương xứng khối
lượng). Vì vậy danh sách dưới đây chỉ gồm **chức năng đã có trong mã nguồn**, cộng
các sửa lỗi nghiệp vụ — không có tính năng mới (D-008). Ngoại lệ duy nhất là việc
hủy đơn ở CN-22, thêm ngày 07/10/2026 theo D-033; nó mở rộng một chức năng đã có
nên tổng số chức năng cam kết không đổi.

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
- `Có` — route và view đã có trong mã nguồn, hành vi khớp đặc tả.
- `Lệch (L-x)` — có, nhưng hành vi đang khác đặc tả vì lỗi L-x chưa xử lý. Chi
  tiết từng lỗi, kể cả lỗi đã sửa, ở [`ISSUES.md`](ISSUES.md).

Hành vi chi tiết của từng chức năng sẽ được kiểm lại khi viết acceptance criteria
ở P-23.

### 2.1 Khách vãng lai và Khách hàng — cửa hàng trực tuyến

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-01 | Đăng ký tài khoản bằng email | UC-01 | Có |
| CN-02 | Đăng nhập | UC-02 | Có |
| CN-03 | Quên mật khẩu — đặt lại qua email | *(chưa có UC)* | Có |
| CN-31 | Đăng xuất (tách khỏi CN-02 ngày 06/11/2026, D-058) | UC-10 | Có |
| CN-04 | Xem trang chủ, danh sách sản phẩm, sản phẩm theo danh mục và theo thẻ | UC-03 | Có |
| CN-05 | Xem chi tiết sản phẩm: giá, mô tả, ảnh, đánh giá, sản phẩm liên quan | UC-04 | Có |
| CN-06 | Tìm sản phẩm theo tên; lọc theo danh mục, nhà cung cấp, khoảng giá | UC-05 | Có |
| CN-07 | Xem danh sách và trang chi tiết nhà cung cấp | *(chưa có UC)* | Có |
| CN-08 | Giỏ hàng: thêm, cập nhật số lượng, xóa; không cho vượt tồn kho | UC-06 | Có |
| CN-09 | Đổi ngôn ngữ vi ↔ en | UC-07 | Có |
| CN-10 | Gửi liên hệ tới ban quản trị | UC-08 | Có |
| CN-11 | Thanh toán: nhập thông tin giao hàng, áp mã giảm giá, chọn COD hoặc VNPay | UC-09 | Có |
| CN-12 | Cập nhật hồ sơ cá nhân, đổi mật khẩu | UC-11 | Có |
| CN-13 | Danh sách yêu thích: thêm, xem, xóa | UC-12 | Có |
| CN-14 | Xem lịch sử đơn mua và chi tiết từng đơn | UC-13 | Có |
| CN-15 | Đánh giá và chấm điểm sản phẩm (1–5 sao) | UC-14 | Có |

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
| CN-20 | Dashboard: doanh thu, doanh thu theo tháng, số đơn, khách hàng mới; doanh thu không tính đơn đã hủy | UC-26 | Có |
| CN-21 | Quản lý sản phẩm: thêm, sửa, xóa mềm, cập nhật tồn kho, quản lý ảnh | UC-19 | Có |
| CN-22 | Quản lý đơn hàng: xem, đổi trạng thái giao hàng, hủy đơn khi khách báo; không có thao tác xóa đơn | UC-20 | Có |
| CN-23 | Xem danh sách đánh giá | *(chưa có UC)* | Có |
| CN-32 | Cập nhật hồ sơ và đổi mật khẩu nhân viên (tách khỏi CN-23 ngày 06/11/2026, D-058) | *(chưa có UC)* | Có |

### 2.4 Quản trị viên — Django admin

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-24 | Quản lý mã giảm giá: tạo, sửa, bật/tắt, xóa mềm và khôi phục | UC-21 | Có |
| CN-25 | Quản lý người dùng: tra cứu, phân quyền, khóa tài khoản | UC-22 | Có |
| CN-26 | Quản lý danh mục: thêm, sửa, xóa mềm và khôi phục | UC-23 | Có |
| CN-27 | Quản lý toàn bộ sản phẩm: đổi trạng thái hiển thị, xóa mềm và khôi phục | UC-24 | Có |
| CN-28 | Tra cứu toàn bộ đơn hàng, lọc theo trạng thái thanh toán và giao hàng | UC-25 | Có |
| CN-29 | Quản lý nhà cung cấp: thêm, sửa, xóa mềm và khôi phục | *(chưa có UC)* | Có |
| CN-30 | Xem hộp thư liên hệ | *(chưa có UC)* | Có |

**Tổng: 32 chức năng**, mỗi chức năng ứng với đúng một use case. Trước ngày 06/11/2026
danh sách có 30 chức năng; CN-02 và CN-23 khi đó mỗi mục gộp hai use case, nay tách
thành CN-31 và CN-32, mã cũ không đánh lại (D-058). Các dòng dưới đây viết trước ngày
đó: "CN-23" trong đó chỉ cả trang đánh giá lẫn trang hồ sơ nhân viên (L-45, L-50, L-51
thuộc phần nay là CN-32). Ngày 05/11/2026 có 30/30 `Có`, ngày 06/11/2026 có 32/32 `Có`. Lượt rà form ngày 05/11/2026 (P-45)
làm CN-10, CN-11, CN-15, CN-21, CN-23 thành `Lệch` (L-45, L-49, L-50, L-51, L-53); sửa ở
local cùng ngày, cả năm về `Có`, chưa thử trên host. Lỗi còn mở không làm chức năng nào lệch
đặc tả: L-24 chưa xảy ra khi host chạy một worker; L-47, L-55 → L-58 là chữ lẫn ngôn ngữ và
nội dung mẫu của theme (P-46). CN-19 và CN-28 về `Có` sau khi sửa L-41 và L-40 (P-43); CN-03
về `Có` sau khi sửa L-43 (P-44).
CN-14 trước đây có thêm "đặt địa chỉ mặc định"; chức năng đó không có giao diện
nên đã bỏ khỏi cam kết (L-33, D-047). Các chức
năng CN-03, 07, 23, 29, 30, 32 có trong mã nguồn nhưng đặc tả TLCN chưa có use case;
sẽ bổ sung UC ở P-23.

---

## 3. Lỗi và chỗ lệch

Từ ngày 03/11/2026, lỗi và chỗ lệch giữa đặc tả với mã nguồn (L-1 trở đi) ghi ở
[`ISSUES.md`](ISSUES.md) (D-046). Bản cam kết chỉ giữ hệ quả lên từng chức năng:
cột Hiện trạng ở §2.

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

| Metric | Công cụ và cách đo | Ngưỡng | Số đo 24/09/2026 | Số đo 02/11/2026 |
|---|---|---|---|---|
| Lỗi lint | Ruff, bộ luật ghi trong `grocerly/ruff.toml` | 0 | 0 (30 trước khi sửa) | 0 |
| Issue Blocker/Critical | Ruff, quy đổi theo danh sách dưới đây | 0 | 0 (5 trước khi sửa) | 0 |
| Tỉ lệ dòng trùng lặp | jscpd, trên mã Python của ứng dụng | ≤ 3% | 1,09% | 0,71% |

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

- **KPI nghiệp vụ** (2-3 KPI định lượng, đủ Mức 3-4 của TC1): ví dụ tỉ lệ trợ lý
  AI chọn đúng sản phẩm và số lượng trên bộ 20-30 câu mẫu (P-42), tỉ lệ người thử
  tự đặt xong đơn trong buổi thực nghiệm, thời gian từ lúc tìm sản phẩm tới lúc
  đặt hàng.
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
