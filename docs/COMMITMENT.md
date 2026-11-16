# BẢN CAM KẾT SẢN PHẨM — Grocerly (KLTN)

> **⚠️ BẢN NHÁP — chưa ký.** Soạn ngày 10/09/2026 để trao đổi với GVHD. Phần
> chức năng (§2) đã đối chiếu với mã nguồn; phần metric và KPI (§5) có mục chất
> lượng mã nguồn (§5.1, soạn ngày 24/09/2026), KPI nghiệp vụ (§5.2, 12/11/2026) và
> các metric còn lại (§5.3, 16/11/2026). Bản trình ký là file Word soạn từ file này,
> viết lại cho GVHD đọc, không dùng mã tra cứu của repo.

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

Hành vi chi tiết của từng chức năng là acceptance criteria của use case tương ứng,
ở [`SRS.md`](SRS.md) §6.2 và §6.3 (P-23, D-061).

### 2.1 Khách vãng lai và Khách hàng — cửa hàng trực tuyến

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-01 | Đăng ký tài khoản bằng email | UC-01 | Có |
| CN-02 | Đăng nhập | UC-02 | Có |
| CN-03 | Quên mật khẩu — đặt lại qua email | UC-27 | Có |
| CN-31 | Đăng xuất (tách khỏi CN-02 ngày 06/11/2026, D-058) | UC-10 | Có |
| CN-04 | Xem trang chủ, danh sách sản phẩm, sản phẩm theo danh mục và theo thẻ | UC-03 | Có |
| CN-05 | Xem chi tiết sản phẩm: giá, mô tả, ảnh, đánh giá, sản phẩm liên quan | UC-04 | Có |
| CN-06 | Tìm sản phẩm theo tên; lọc theo danh mục, nhà cung cấp, khoảng giá | UC-05 | Có |
| CN-07 | Xem danh sách và trang chi tiết nhà cung cấp | UC-28 | Có |
| CN-08 | Giỏ hàng: thêm, cập nhật số lượng, xóa; không cho vượt tồn kho | UC-06 | Lệch (L-72) |
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
| CN-19 | AI dẫn người dùng tới trang thanh toán | UC-18 | Lệch (L-74) |

*Công cụ `get_bestsellers` (gợi ý sản phẩm "nổi bật") vẫn còn trong mã nguồn nhưng
**không thuộc cam kết**: nó chỉ lấy sản phẩm gắn cờ `featured` thủ công, không tính
doanh số thật.*

### 2.3 Nhân viên cửa hàng — `/useradmin/`

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-20 | Dashboard: doanh thu, doanh thu theo tháng, số đơn, khách hàng mới; doanh thu không tính đơn đã hủy | UC-26 | Lệch (L-76) |
| CN-21 | Quản lý sản phẩm: thêm, sửa, xóa mềm, cập nhật tồn kho, quản lý ảnh | UC-19 | Lệch (L-75) |
| CN-22 | Quản lý đơn hàng: xem, đổi trạng thái giao hàng, hủy đơn khi khách báo; không có thao tác xóa đơn | UC-20 | Có |
| CN-23 | Xem danh sách đánh giá | UC-29 | Có |
| CN-32 | Cập nhật hồ sơ và đổi mật khẩu nhân viên (tách khỏi CN-23 ngày 06/11/2026, D-058) | UC-30 | Có |

### 2.4 Quản trị viên — Django admin

| Mã | Chức năng | UC | Hiện trạng |
|---|---|---|---|
| CN-24 | Quản lý mã giảm giá: tạo, sửa, bật/tắt, xóa mềm và khôi phục | UC-21 | Có |
| CN-25 | Quản lý người dùng: tra cứu, phân quyền, khóa tài khoản | UC-22 | Có |
| CN-26 | Quản lý danh mục: thêm, sửa, xóa mềm và khôi phục | UC-23 | Có |
| CN-27 | Quản lý toàn bộ sản phẩm: đổi trạng thái hiển thị, xóa mềm và khôi phục | UC-24 | Có |
| CN-28 | Tra cứu toàn bộ đơn hàng, lọc theo trạng thái thanh toán và giao hàng | UC-25 | Có |
| CN-29 | Quản lý nhà cung cấp: thêm, sửa, xóa mềm và khôi phục | UC-31 | Có |
| CN-30 | Xem hộp thư liên hệ | UC-32 | Có |

**Tổng: 32 chức năng**, mỗi chức năng ứng với đúng một use case. Trước ngày 06/11/2026
danh sách có 30 chức năng; CN-02 và CN-23 khi đó mỗi mục gộp hai use case, nay tách
thành CN-31 và CN-32, mã cũ không đánh lại (D-058). Các dòng dưới đây viết trước ngày
đó: "CN-23" trong đó chỉ cả trang đánh giá lẫn trang hồ sơ nhân viên (L-45, L-50, L-51
thuộc phần nay là CN-32). Ngày 05/11/2026 có 30/30 `Có`, ngày 06/11/2026 có 32/32 `Có`. Lượt rà form ngày 05/11/2026 (P-45)
làm CN-10, CN-11, CN-15, CN-21, CN-23 thành `Lệch` (L-45, L-49, L-50, L-51, L-53); sửa ở
local cùng ngày, cả năm về `Có`, chưa thử trên host. Lỗi còn mở không làm chức năng nào lệch
đặc tả: L-24 chưa xảy ra khi host chạy một worker; L-47, L-55 → L-58 là chữ lẫn ngôn ngữ và
nội dung mẫu của theme (P-46). CN-19 và CN-28 về `Có` sau khi sửa L-41 và L-40 (P-43); CN-03
về `Có` sau khi sửa L-43 (P-44). Ngày 13/11/2026 CN-08 thành `Lệch (L-72)`: giỏ hàng vẫn nhận và giữ sản phẩm đã gỡ bán, thấy khi vẽ lược đồ tuần tự; còn 31/32 `Có`. Ngày 15/11/2026 CN-19 thành `Lệch (L-74)`: trợ lý vẫn mời thanh toán khi giỏ chỉ còn hàng vừa hết, cũng thấy khi vẽ lược đồ tuần tự; còn 30/32 `Có`. Cùng ngày, vẽ lược đồ phần nhân viên làm CN-21 thành `Lệch (L-75)` (ô tồn kho trên dòng nhận số âm) và CN-20 thành `Lệch (L-76)` (doanh thu theo tháng không xét năm); còn 28/32 `Có`.
CN-14 trước đây có thêm "đặt địa chỉ mặc định"; chức năng đó không có giao diện
nên đã bỏ khỏi cam kết (L-33, D-047). Các chức
năng CN-03, 07, 23, 29, 30, 32 có trong mã nguồn nhưng đặc tả TLCN chưa có use case;
báo cáo KLTN mục 3.2 bổ sung sáu use case đó, trong repo mang mã UC-27 → UC-32 (D-061).

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

## 5. Metric và KPI

### 5.1 Chất lượng mã nguồn (TC2.4)

Ba con số của TC2.4 đều đo bằng công cụ chạy trong CI ở mỗi lần đẩy mã nguồn, nên
có số đo cho từng commit chứ không chỉ một lần cuối kỳ. Ngưỡng đề xuất giữ đúng Mức
5 của rubric, vì số đo hiện tại đã đạt.

| Metric | Công cụ và cách đo | Ngưỡng | Số đo 24/09/2026 | Số đo 02/11/2026 | Số đo 16/11/2026 |
|---|---|---|---|---|---|
| Lỗi lint | Ruff, bộ luật ghi trong `grocerly/ruff.toml` | 0 | 0 (30 trước khi sửa) | 0 | 0 |
| Issue Blocker/Critical | Ruff, quy đổi theo danh sách dưới đây | 0 | 0 (5 trước khi sửa) | 0 | 0 |
| Tỉ lệ dòng trùng lặp | jscpd, trên mã Python của ứng dụng | ≤ 3% | 1,09% | 0,71% | 0,63% |

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
kiểm tra một cách có chủ ý. Template HTML cũng không tính, vì các công cụ rubric nêu
tên đều đo mã của ngôn ngữ lập trình. Bản trình ký chỉ nêu phạm vi này, không ghi số
đo của template: số đó và nguyên nhân trùng ghi ở mục hạn chế của báo cáo, không cam
kết ngưỡng (D-031, cập nhật 16/11/2026).

Kiểm tra lại được bằng hai lệnh chạy trong `grocerly/`: `ruff check .` và `jscpd .`.

### 5.2 KPI nghiệp vụ (TC1)

Ba KPI, nhắm Mức 3-4 của TC1. Cả ba đo cái khách nhận được khi mua hàng, không đo
mã nguồn. KPI đầu đã có số đo; hai KPI sau đo trong buổi thực nghiệm người dùng
(P-25, dự kiến Tuần 11), nên hiện chỉ có ngưỡng. Ngưỡng ở đây là đề xuất, chốt khi
trình GVHD.

| KPI | Cách đo | Ngưỡng | Số đo 12/11/2026 |
|---|---|---|---|
| Trợ lý AI đề nghị đúng sản phẩm và số lượng | 30 câu mẫu trên một danh mục 14 sản phẩm cố định, Gemini thật, `python ai_eval/run_eval.py` (D-062); tính trên mọi lượt chạy trong kỳ | ≥ 85% câu đúng, và ≤ 2/30 câu có đề nghị sai | 28/30 (93,3%) ở cả hai lượt, 1/30 đề nghị sai |
| Người thử tự đặt xong đơn | Mỗi người thử làm một tác vụ mua hàng có trợ lý AI, không được ai chỉ; đơn tạo ra trong database là xong | ≥ 60% số người thử | Chưa đo |
| Thời gian từ lúc tìm sản phẩm tới lúc đặt hàng | Bấm giờ trong cùng tác vụ trên, từ khi mở trang tới khi thấy trang đặt hàng thành công; lấy trung vị | ≤ 5 phút | Chưa đo |

Vài điều về KPI đầu. "Đề nghị sai" là khi khách thấy nút xác nhận với sai sản phẩm
hay sai số lượng; đó là lỗi đáng ngại, nên có ngưỡng riêng. Câu trượt vì Gemini hỏi
lại bằng lời thì khách không thấy gì sai. Ngưỡng 85% thấp hơn số đo vì Gemini trả lời
mỗi lần một khác, và số đo đi qua cả việc chuyển sang model dự phòng khi model đầu
quá tải (D-060), y như trên host. Ngoài bộ cố định, 12 câu hợp với danh mục thật của
host cũng được thử ngày 12/11/2026, chỉ chat, không bấm xác nhận: 12/12.

KPI thứ hai lấy ngưỡng theo Mức 3 của TC2.7 (tác vụ thành công ≥ 60%), vì buổi thực
nghiệm có khoảng 3-5 người, mỗi người lệch một là 20-33%. Ngưỡng 5 phút của KPI thứ
ba là ước lượng, chưa có ai bấm giờ cả tác vụ: số đo gần nhất chỉ là mỗi tin nhắn
với trợ lý trên host mất 1 - 15 giây (lượt đối chiếu 12/11/2026), phần lớn thời gian
còn lại là người lần đầu dùng trang tự tìm đường. Số đo lệch
xa ngưỡng thì ghi vào hạn chế, không đổi ngưỡng sau khi đã đo.

### 5.3 Các metric còn lại

Ngưỡng ở bảng dưới lấy theo Mức 4 của bảng tham chiếu trong rubric Mục 5. Riêng
thực nghiệm người dùng và số bên liên quan lấy Mức 3, vì buổi thực nghiệm chỉ có
khoảng 3-5 người (D-017) và phần phỏng vấn gộp vào buổi đó (D-013). Ngưỡng là mức
chắc chắn giữ được tới ngày bảo vệ, nên nhiều số đo hôm nay đã vượt xa ngưỡng mà
ngưỡng không nâng theo. Ba metric ở §5.1 giữ Mức 5 vì CI chặn ngay khi vượt: còn
một lỗi lint hay trùng lặp quá 3% là không merge được.

Số đo 16/11/2026: bộ test chạy ở máy làm việc, CI và deploy đếm bằng `gh` trên
GitHub cùng ngày.

| Nhóm | Metric | Cách đo | Ngưỡng | Số đo 16/11/2026 |
|---|---|---|---|---|
| TC2.1 | Use case có acceptance criteria | `SRS.md` §6.2, §6.3 | ≥ 80% | 32/32 (100%), 91 tiêu chí |
| TC2.1 | Loại sơ đồ thiết kế, khớp mã nguồn | Báo cáo KLTN chương 3; hội đồng đối chiếu 5 điểm | ≥ 3 loại, khớp ≥ 80% | 4 loại: lớp, tuần tự (cho cả 32 use case), kiến trúc tổng thể, triển khai. Use case và trạng thái đơn hàng có vẽ nhưng không tính |
| TC2.1 | Yêu cầu phi chức năng có ràng buộc định lượng | `SRS.md` §5 | ≥ 3 | 3, cả ba đạt khi đo trên host ngày 05/11/2026 |
| TC2.2 | Chức năng cam kết hoạt động | 32 chức năng ở §2, chạy trên host | ≥ 85% (≥ 28/32) | 32/32 chạy được; 28/32 khớp đặc tả, 4 lệch ở chi tiết (cột Hiện trạng) |
| TC2.2 | Lỗi chặn khi demo | Ghi nhận của hội đồng | ≤ 1 | Chưa demo |
| TC2.2 | Môi trường sản phẩm | URL công khai | Staging công khai | `grocerly-v2.onrender.com`, chạy từ 15/10/2026 |
| TC2.3 | AI Usage Log | `AI_USAGE_LOG.md` | Đủ các mục, đối chiếu được với commit | Có từ phiên đầu tiên (10/09/2026), mỗi dòng ghi commit chứa nó |
| TC2.3 | Lỗi của AI tự phát hiện và sửa | `AI_USAGE_LOG.md` §2 | ≥ 3, có phân tích nguyên nhân | 89 |
| TC2.4 | Tuần có commit | Lịch sử Git | ≥ 75% (≥ 12/15 tuần) | 9/9 tuần đã qua (Tuần 1 → Tuần 9), cộng tuần chuẩn bị |
| TC2.4 | Thay đổi đi qua Pull Request có review | Lịch sử PR trên GitHub, theo cách hiểu ở dưới bảng | ≥ 60% | 18/28 PR (64%); tính từ PR #8, lúc bắt đầu review, là 18/21 |
| TC2.4 | Secret lộ trong repository | gitleaks trên toàn bộ lịch sử, mỗi lần CI chạy | 0 | 0 |
| TC2.5 | Độ phủ dòng lệnh của mô-đun cốt lõi | `pytest --cov` trên bốn app `core`, `userauths`, `useradmin`, `store_api`, không tính migration và test (như NFR-04) | ≥ 70% | 93%; bốn file `views.py`: 89%, 97%, 93%, 95% |
| TC2.5 | Số tầng kiểm thử | Mã test | ≥ 2 | 3: unit và tích hợp (pytest-django), API (gọi endpoint `/api/v1/` qua test client, Gemini giả lập), trình duyệt thật (Playwright) |
| TC2.5 | Tỉ lệ test case tự động | Bộ test | ≥ 50% | 100%: năm kịch bản thủ công của TLCN đều đã thành test tự động |
| TC2.5 | Test pass ở lần chạy CI cuối | Log CI | ≥ 95% | 100% ở lần chạy 15/11/2026 trên `develop`. Bộ test thường: 501 passed, 10 `xfail` là lỗi đã biết còn mở; 29 test trình duyệt chạy ở bước riêng |
| TC2.5 | Defect Critical/Blocker còn tồn | `ISSUES.md` | ≤ 1 | 0 (5 lỗi mở, không lỗi nào thuộc hai mức này, định nghĩa ở dưới bảng) |
| TC2.6 | Số chặng của pipeline | `.github/workflows/ci.yml` | ≥ 4 | 6: build (`check`, `makemigrations --check`), lint và phân tích tĩnh, test kèm độ phủ, quét secret, quét thư viện có lỗ hổng, deploy. Không đóng gói Docker |
| TC2.6 | Tỉ lệ build xanh | Lịch sử run của `ci.yml` | ≥ 80% | 113/116 (97%) |
| TC2.6 | Số lần deploy tự động | GitHub Deployments, môi trường `production` | ≥ 5 | 18 |
| TC2.6 | Thời gian từ merge tới khi host chạy commit mới | Log CI, health trả SHA | ≤ 30 phút | Khoảng 4 phút |
| TC2.6 | Giám sát sau deploy | Cấu hình | Health check | Health check, log lỗi ra Render, `health.yml` gọi mỗi giờ và gửi thư khi đỏ |
| TC2.7 | Người dùng thật thuộc nhóm đối tượng | Danh sách ẩn danh, biên bản | ≥ 3, nhắm 5 | Chưa làm, dự kiến Tuần 11 |
| TC2.7 | Tỉ lệ hoàn thành tác vụ | Biên bản thực nghiệm | ≥ 60% | Chưa làm; trùng KPI thứ hai ở §5.2 |
| TC2.7 | Điểm SUS | Phiếu SUS 10 câu | ≥ 55 | Chưa làm |
| TC2.7 | Vòng cải tiến có đo lại | Báo cáo thực nghiệm | Không cam kết | Lỗi người thử gặp thì ghi vào `ISSUES.md` và sửa nếu kịp |
| TC1 | Bên liên quan được phỏng vấn | Biên bản phần phỏng vấn của buổi thực nghiệm | ≥ 1, nhắm 3 | Chưa làm |
| TC1 | Giải pháp hiện có được so sánh | `SRS.md` §1.1, báo cáo mục 1.1 | ≥ 2 | 3: Bách Hóa Xanh, Co.op Online, Shopee |
| TC1 | KPI nghiệp vụ định lượng | §5.2 | ≥ 3 | 3 |
| Quy trình | Báo cáo tiến độ | Portal | ≥ 1 lần/tuần | Mọi tuần từ tuần chuẩn bị tới Tuần 9 |

Trong bảng có hai ngưỡng cao hơn Mức 4, cả hai để khớp NFR đã ghi từ 05/11/2026:
secret lộ giữ 0 như NFR-03, độ phủ giữ 70% như NFR-04 thay vì 50%. Ba tiêu chí
TC3, TC4, TC5 chấm ở buổi bảo vệ theo ngưỡng chung của rubric, không điều chỉnh ở
đây.

**Pull Request có review, cho đồ án một người** (D-016, giữ cách hiểu của D-012).
Mọi thay đổi vào `main` đi qua PR từ `develop`. Một PR tính là có review khi có đủ
ba thứ: CI xanh trên PR; một lượt review do một agent AI riêng đọc diff, đăng thành
review hay comment trên PR; và câu trả lời của sinh viên cho từng điểm, sửa ngay
trong PR nếu cần. GitHub không cho tác giả tự bấm Approve, nên không tính lượt
Approve. PR #1 → #7 merge trước khi có CI và quy trình này.

**Defect Critical/Blocker.** Quy đổi theo cùng tinh thần với §5.1: Blocker là lỗi
chặn hẳn một luồng chính (đăng nhập, mua hàng, thanh toán, quản lý đơn) hoặc làm
sập trang; Critical là lỗi làm sai tiền, lộ dữ liệu hay cho người không có quyền
làm thao tác ghi. Năm lỗi đang mở đều không thuộc hai mức này: L-24 chỉ xảy ra khi
host chạy nhiều worker, L-72, L-74, L-75, L-76 là chi tiết lệch đặc tả.

**Ý kiến bên liên quan** (D-013). Không làm đợt khảo sát riêng. Mỗi buổi thực
nghiệm dành khoảng 5 phút đầu hỏi người thử về thói quen mua thực phẩm, rồi mới làm
tác vụ và chấm SUS; biên bản ghi tách hai phần. Vì vậy số bên liên quan bằng số
người thử, và dữ liệu nhu cầu tới sau ngày chốt KPI: phần phỏng vấn dùng để kiểm
chứng lại ba KPI ở §5.2, không dùng để chọn KPI.

---

## 6. Xác nhận

| Sinh viên | Giảng viên hướng dẫn |
|---|---|
| | |
| Lê Đức Phát | Hoàng Văn Dũng |
| Ngày: | Ngày: |
