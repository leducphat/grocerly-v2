# ĐỀ CƯƠNG KHÓA LUẬN TỐT NGHIỆP — Grocerly

> **⚠️ BẢN NHÁP — chưa ký.** Soạn ngày 11/09/2026 theo khung *"Đề cương báo cáo
> môn học"* của TLCN, để trình GVHD. Đề cương là văn bản **đăng ký ban đầu**; tiến
> độ thực tế theo dõi ở [`PLAN.md`](PLAN.md), danh sách chức năng và ngưỡng metric
> chính thức nằm ở bản cam kết [`COMMITMENT.md`](COMMITMENT.md) (P-03).
>
> Theo ý kiến GVHD cho bản nộp Tuần 1, đề cương được nộp để GVHD **góp ý nội
> dung** cùng báo cáo Tuần 2 — hạn **17:00 Thứ Sáu 18/09/2026** (P-08).

**Trường ĐH Công nghệ Kỹ thuật TP.HCM — Khoa Công nghệ Thông tin**

| | |
|---|---|
| Họ và tên SV thực hiện | **Lê Đức Phát** — MSSV **21139083** |
| Chuyên ngành | **Công nghệ Phần mềm** |
| Thời gian làm đồ án | **Từ 07/09/2026 đến 20/12/2026** (15 tuần) |
| Tên đề tài | **Xây dựng website bán thực phẩm tích hợp trợ lý AI tự động đặt hàng** |
| GV hướng dẫn | **Hoàng Văn Dũng** |
| GV phản biện | **Hoàng Thái Xuân Khoa** |

---

## 1. Dữ liệu và tài liệu ban đầu

- **Sản phẩm và báo cáo TLCN cùng đề tài, cùng GVHD, đã chấm điểm:** mã nguồn
  website Grocerly (Django) trên GitHub; đặc tả 26 use case, ERD 14 bảng, 27 màn
  hình và 5 test case kiểm thử thủ công. KLTN kế thừa sản phẩm này, không xây lại
  từ đầu.
- **Các hạn chế TLCN đã tự ghi nhận:** chưa có kiểm thử tự động, chưa có CI/CD,
  chưa thực nghiệm với người dùng thật, đặc tả chưa có acceptance criteria và
  chưa được đối chiếu lại với mã nguồn.
- **Rubric chấm điểm KLTN** của Khoa CNTT — chuyên ngành Công nghệ Phần mềm.
- **Người dùng thực tế:** khoảng 3–5 người thuộc nhóm đối tượng mua thực phẩm
  trực tuyến, tham gia phỏng vấn nhu cầu và thực nghiệm sản phẩm.
- **Tài liệu chuyên ngành, ưu tiên tài liệu ngoại ngữ:** tài liệu chính thức của
  Django, pytest / pytest-django, coverage.py, GitHub Actions, Google Gemini API
  (function calling); OWASP Top 10; chuẩn chất lượng phần mềm ISO/IEC 25010; thang
  đo khả dụng SUS (System Usability Scale).

## 2. Nhiệm vụ của khóa luận

### 2.1. Về mặt lý thuyết

- Tìm hiểu quy trình phát triển hướng đặc tả (Spec Driven Development): đặc tả yêu
  cầu (SRS), đặc tả thiết kế (SDD), viết acceptance criteria kiểm chứng được.
- Nghiên cứu kiểm thử phần mềm tự động: kiểm thử đơn vị và tích hợp với pytest +
  pytest-django, thiết kế ca âm và ca biên, đo độ phủ mã nguồn.
- Nghiên cứu quy trình tích hợp và triển khai liên tục (CI/CD) với GitHub Actions:
  build, lint, test, quét secret, đóng gói, triển khai; giám sát sau triển khai
  (health check, log).
- Tìm hiểu các phương pháp quản lý chất lượng mã nguồn: linter, phân tích tĩnh,
  quy trình làm việc theo nhánh và Pull Request.
- Tìm hiểu các lỗ hổng bảo mật ứng dụng web phổ biến (OWASP Top 10), đặc biệt là
  tin tưởng dữ liệu phía máy khách và kiểm soát truy cập.
- Tìm hiểu cơ chế function calling của mô hình ngôn ngữ lớn (Google Gemini) và
  cách ràng buộc để AI không tự ý thay đổi dữ liệu của người dùng.
- Nghiên cứu phương pháp thực nghiệm người dùng và đánh giá khả dụng bằng thang SUS.

### 2.2. Về mặt thực hành

- **Chốt bản cam kết sản phẩm và bộ metric** với GVHD trước **25/10/2026** (hết
  Tuần 7, mốc 50% thời gian): 30 chức năng cam kết, ngưỡng metric kỹ thuật và
  ≥ 5 KPI nghiệp vụ.
- **Hoàn thiện đặc tả và thiết kế:**
  - Tách đặc tả thành SRS (yêu cầu) và SDD (thiết kế).
  - Đối chiếu đặc tả TLCN với mã nguồn, sửa những chỗ sai hoặc lỗi thời, ghi lại
    từng lần sửa kèm lý do.
  - Viết acceptance criteria cho 100% use case; bổ sung use case cho các chức năng
    đã có trong mã nguồn nhưng chưa được đặc tả.
  - Định lượng hóa ≥ 5 yêu cầu phi chức năng.
  - Cập nhật ≥ 4 loại sơ đồ (Use Case, tuần tự, lớp, ERD) cho khớp mã nguồn.
- **Củng cố chất lượng sản phẩm:** sửa các lỗi nghiệp vụ phát hiện khi đối chiếu
  đặc tả với mã nguồn. Ưu tiên cao nhất là lỗi giá sản phẩm do trình duyệt gửi
  lên; tiếp theo là kiểm tra tồn kho ở server, chỉ cho đánh giá sản phẩm đã mua,
  chặn đổi trạng thái đơn đã giao. Mỗi lần sửa kèm test tái hiện lỗi.
- **Kiểm thử tự động:** viết test cho các luồng cốt lõi (xác thực, giỏ hàng, đặt
  hàng và thanh toán, công cụ của trợ lý AI), báo cáo độ phủ trong CI.
- **CI/CD và triển khai:** dựng pipeline nhiều chặng, triển khai lên hạ tầng riêng
  của KLTN (host, cơ sở dữ liệu, lưu trữ ảnh tách khỏi TLCN), bổ sung health check
  và log sau triển khai.
- **Thực nghiệm người dùng:** khoảng 3–5 người thật; mỗi buổi gồm phỏng vấn nhu
  cầu, thực hiện tác vụ và chấm SUS; sau đó cải tiến theo phản hồi và đo lại
  trước–sau.
- **Quy trình và minh chứng:** làm việc theo nhánh + Pull Request; commit và báo
  cáo tiến độ với GVHD hằng tuần; ghi nhật ký sử dụng AI (AI Usage Log) ngay sau
  mỗi phiên làm việc.

## 3. Sản phẩm dự kiến đạt được

- Website Grocerly phiên bản KLTN theo mô hình một cửa hàng bán hàng của nhiều nhà
  cung cấp, **30 chức năng đã cam kết hoạt động đúng đặc tả**, triển khai công khai
  trên hạ tầng riêng, có trợ lý AI tìm sản phẩm, đề xuất thêm vào giỏ và dẫn tới
  thanh toán.
- Bộ tài liệu SRS và SDD khớp với mã nguồn, có acceptance criteria truy vết được
  tới test.
- Bộ kiểm thử tự động kèm báo cáo độ phủ; pipeline CI/CD kèm lịch sử chạy và lịch
  sử triển khai tích lũy suốt quá trình làm.
- Báo cáo thực nghiệm người dùng: biên bản từng buổi, điểm SUS trước và sau cải
  tiến, đối chiếu với KPI đã cam kết.
- Hồ sơ minh chứng quá trình: báo cáo tuần, nhật ký quyết định, AI Usage Log.
- Quyển báo cáo khóa luận tốt nghiệp.

Ngưỡng định lượng cụ thể (độ phủ, số chặng CI/CD, số lần triển khai, số người dùng
thực nghiệm, điểm SUS…) được chốt trong bản cam kết, không ghi cứng ở đề cương.

## 4. Bố cục dự kiến của quyển báo cáo

**1. PHẦN MỞ ĐẦU**

- 1.1. Tính cấp thiết của đề tài
- 1.2. Kế thừa từ Tiểu luận chuyên ngành và điểm mới của khóa luận
- 1.3. Mục tiêu và phạm vi nghiên cứu
- 1.4. Phương pháp thực hiện

**2. PHẦN NỘI DUNG**

Chương 1: Khảo sát hiện trạng và phân tích yêu cầu

- 1.1. Phân tích một số hệ thống có liên quan trên thị trường
- 1.2. Khảo sát nhu cầu người dùng thực tế
- 1.3. Yêu cầu chức năng
- 1.4. Yêu cầu phi chức năng
- 1.5. Chỉ số đánh giá nghiệp vụ (KPI)

Chương 2: Cơ sở lý thuyết và công nghệ sử dụng

- 2.1. Các công nghệ phát triển hệ thống (Front-end, Back-end, cơ sở dữ liệu)
- 2.2. Tích hợp mô hình ngôn ngữ lớn và cơ chế function calling
- 2.3. Kiểm thử phần mềm tự động
- 2.4. Tích hợp và triển khai liên tục (CI/CD)
- 2.5. Quản lý chất lượng mã nguồn
- 2.6. Đánh giá khả dụng phần mềm

Chương 3: Phân tích và thiết kế hệ thống

- 3.1. Lược đồ Use Case
- 3.2. Đặc tả Use Case và tiêu chí chấp nhận
- 3.3. Lược đồ tuần tự
- 3.4. Lược đồ lớp
- 3.5. Thiết kế cơ sở dữ liệu mức vật lý (ERD)
- 3.6. Kiến trúc hệ thống và thiết kế trợ lý AI
- 3.7. Thiết kế giao diện (UI/UX)
- 3.8. Đối chiếu đặc tả TLCN với mã nguồn và các chỉnh sửa

Chương 4: Cài đặt, kiểm thử và triển khai

- 4.1. Cài đặt môi trường
- 4.2. Quy trình phát triển: nhánh, Pull Request và review
- 4.3. Kiểm thử tự động và độ phủ mã nguồn
- 4.4. Pipeline CI/CD và triển khai
- 4.5. Giám sát sau triển khai
- 4.6. Bảo mật: quét secret và xử lý lỗ hổng
- 4.7. Kiểm soát việc sử dụng AI trong quá trình phát triển

Chương 5: Thực nghiệm với người dùng

- 5.1. Kế hoạch thực nghiệm (đối tượng, tác vụ, thang đo)
- 5.2. Kết quả thực nghiệm vòng 1
- 5.3. Cải tiến theo phản hồi và kết quả đo lại
- 5.4. Đánh giá theo KPI đã cam kết

**3. PHẦN KẾT LUẬN**

- 1. Kết quả đạt được
- 2. Ưu điểm và nhược điểm
- 3. Các hướng phát triển mở rộng

**4. TÀI LIỆU THAM KHẢO**

**5. PHỤ LỤC** — bản cam kết sản phẩm và metric, AI Usage Log, biên bản thực
nghiệm người dùng, sổ theo dõi tiến độ.

## 5. Kế hoạch thực hiện

Lịch từng tuần: [`PLAN.md`](PLAN.md) §2. Mã `P-xx`
tra trong backlog [`PLAN.md`](PLAN.md) §4.

| STT | Thời gian dự kiến | Nội dung công việc | Ghi chú |
|---|---|---|---|
| 1 | Tuần 1 – Tuần 2 (07/09 – 20/09/2026) | Rà soát rubric và hiện trạng repo. Dựng khung tài liệu đặc tả. Soạn nháp bản cam kết sản phẩm. Tách SRS/SDD. Chuyển sang làm việc theo nhánh + Pull Request. | P-01 → P-07 |
| 2 | Tuần 3 – Tuần 4 (21/09 – 04/10/2026) | Dựng hạ tầng riêng cho KLTN. Dựng pipeline CI. Cài pytest, viết những test đầu tiên. Cấu hình linter, phân tích tĩnh và quét secret trong CI. | P-10, P-11, P-12, P-14, P-15 |
| 3 | Tuần 5 – Tuần 7 (05/10 – 25/10/2026) | Viết test cho luồng cốt lõi, đưa báo cáo độ phủ vào CI. Sửa lỗi giá và lỗi tồn kho kèm test tái hiện lỗi. Định lượng NFR. Soạn metric, KPI và **ký bản cam kết**. | P-12, P-13, P-21, P-03. **Hạn 25/10/2026** |
| 4 | Tuần 8 – Tuần 9 (26/10 – 08/11/2026) | Rà soát đặc tả và viết acceptance criteria cho từng use case. Cập nhật sơ đồ thiết kế cho khớp mã nguồn. Sửa các lỗi nghiệp vụ còn lại. Bổ sung health check và log. | P-23, P-24, P-16 |
| 5 | Tuần 10 – Tuần 12 (09/11 – 29/11/2026) | Chuẩn bị kịch bản thực nghiệm. Thực nghiệm với khoảng 3–5 người dùng: phỏng vấn nhu cầu, thực hiện tác vụ, chấm SUS. | P-25. Xong trong Tuần 12 |
| 6 | Tuần 12 – Tuần 13 (23/11 – 06/12/2026) | Cải tiến theo phản hồi, đo lại trước–sau. Bắt đầu viết báo cáo khóa luận. | P-26, P-30 |
| 7 | Tuần 14 – Tuần 15 (07/12 – 20/12/2026) | Hoàn thiện báo cáo và mục hướng phát triển mở rộng. Kiểm tra trùng lặp. Chuẩn bị slide và demo trực tiếp. Tổng hợp hồ sơ minh chứng. | P-30 → P-34 |
| — | Suốt 15 tuần | Commit và báo cáo tiến độ với GVHD hằng tuần, nộp portal trước 17:00 Thứ Sáu; ghi AI Usage Log sau mỗi phiên làm việc. | P-05 |

---

*Tp. Hồ Chí Minh, ngày … tháng … năm 2026*

| Ý kiến của giáo viên hướng dẫn | Người viết đề cương |
|---|---|
| | |
| *(ký và ghi rõ họ tên)* | *(ký và ghi rõ họ tên)* |
| Hoàng Văn Dũng | Lê Đức Phát |
