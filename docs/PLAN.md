# PLAN — Grocerly (KLTN)

Kế hoạch cải tiến và theo dõi tiến độ. Cập nhật khi trạng thái thay đổi, không
chờ tới cuối kỳ.

| | |
|---|---|
| Cập nhật lần cuối | 21/09/2026 |
| Đặc tả tham chiếu | [`SRS.md`](SRS.md) (yêu cầu), [`SDD.md`](SDD.md) (thiết kế) |
| Quyết định liên quan | [`DECISIONS.md`](DECISIONS.md) — D-005 (thứ tự ưu tiên), D-008 (phạm vi), D-011 (tách SRS/SDD ngay từ đầu), D-016 (làm trên `develop`, merge vào `main` qua PR — thay D-012), D-013 (gộp khảo sát vào thực nghiệm), D-017 (thực nghiệm với khoảng 3–5 người dùng), D-022 (giá giỏ hàng đọc từ database — sửa L-6), D-023 (chỉ VNPay xác nhận đơn đã thanh toán — sửa L-8), D-024 (giỏ hàng hạ số lượng xuống bằng tồn kho — sửa L-7) |

---

## 1. Mục tiêu KLTN

KLTN kế thừa sản phẩm TLCN đã hoàn chỉnh và đã có điểm. Trọng tâm là **làm chắc
phần cốt lõi đã có**, không mở rộng tính năng:

1. **Chuyên nghiệp hóa kỹ thuật phần mềm** — kiểm thử tự động, CI/CD, quản lý chất
   lượng mã nguồn, thực nghiệm với người dùng thật. Đây là phần TLCN gần như không
   có, và cũng là phần rubric KLTN chấm nặng nhất (TC2.4 + TC2.5 + TC2.6 + TC2.7 =
   25/100 điểm).
2. **Hoàn thiện đặc tả** — viết acceptance criteria, định lượng hóa NFR, sửa các
   chỗ sai/lỗi thời trong đặc tả TLCN, cập nhật sơ đồ cho khớp mã nguồn.
3. **Củng cố chất lượng sản phẩm** — xử lý ngoại lệ, ca biên, phân quyền, ghi log.

**Ngoài phạm vi.** Tìm kiếm full-text, thống kê đa chiều nâng cao, live chat thời
gian thực, gợi ý bằng Machine Learning, mobile app, mô hình nhiều người bán
(marketplace) — tất cả thuộc mục *"Các hướng phát triển mở rộng"* ở cuối báo cáo,
không làm trong KLTN. Xem D-008, D-015.

---

## 2. Lịch thực hiện

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| GV phản biện | Hoàng Thái Xuân Khoa |

Đồ án chạy **15 tuần**, đánh số **Tuần 1 → Tuần 15**; mỗi tuần bắt đầu Thứ Hai.

| Mốc | Tuần | Ngày | Ghi chú |
|---|---|---|---|
| Bắt đầu | Tuần 1 | 07/09/2026 – 13/09/2026 | |
| Hết Giai đoạn 0 | Tuần 4 | 28/09/2026 – 04/10/2026 | |
| **Chốt cam kết sản phẩm + bộ metric** | **hết Tuần 7** | **25/10/2026** | **Mốc 50%. Gate G1 — trễ là *không đủ điều kiện bảo vệ*.** |
| Xong thực nghiệm người dùng | Tuần 12 | 23/11/2026 – 29/11/2026 | |
| Hoàn tất báo cáo | Tuần 15 | 14/12/2026 – 20/12/2026 | |
| Phản biện | — | Dự kiến tháng 12/2026 | |

**Nhịp bắt buộc:** báo cáo tiến độ với GVHD ≥ 1 lần/tuần, nộp lên portal **trước
17:00 Thứ Sáu** của chính tuần đó (GVHD chốt, áp dụng từ Tuần 2). Dưới 0,5
lần/tuần → gate **G2** → TC2.2 và TC2.4 mỗi tiêu chí bị hạ một mức. Báo cáo tuần
**không nằm trong repo** — xem [`DECISIONS.md`](DECISIONS.md) D-021.

### Lịch 15 tuần và hạn nộp portal

| Tuần | Từ | Đến | Hạn nộp portal (trước 17:00) |
|---|---|---|---|
| 1 | 07/09/2026 | 13/09/2026 | — *(đã nộp 12/09, trước khi có hạn)* |
| 2 | 14/09/2026 | 20/09/2026 | Thứ Sáu 18/09/2026 |
| 3 | 21/09/2026 | 27/09/2026 | Thứ Sáu 25/09/2026 |
| 4 | 28/09/2026 | 04/10/2026 | Thứ Sáu 02/10/2026 |
| 5 | 05/10/2026 | 11/10/2026 | Thứ Sáu 09/10/2026 |
| 6 | 12/10/2026 | 18/10/2026 | Thứ Sáu 16/10/2026 |
| **7** | **19/10/2026** | **25/10/2026** | Thứ Sáu 23/10/2026 — **hạn chốt cam kết sản phẩm + metric** |
| 8 | 26/10/2026 | 01/11/2026 | Thứ Sáu 30/10/2026 |
| 9 | 02/11/2026 | 08/11/2026 | Thứ Sáu 06/11/2026 |
| 10 | 09/11/2026 | 15/11/2026 | Thứ Sáu 13/11/2026 |
| 11 | 16/11/2026 | 22/11/2026 | Thứ Sáu 20/11/2026 |
| 12 | 23/11/2026 | 29/11/2026 | Thứ Sáu 27/11/2026 |
| 13 | 30/11/2026 | 06/12/2026 | Thứ Sáu 04/12/2026 |
| 14 | 07/12/2026 | 13/12/2026 | Thứ Sáu 11/12/2026 |
| 15 | 14/12/2026 | 20/12/2026 | Thứ Sáu 18/12/2026 |

Việc làm sau lúc nộp (tối Thứ Sáu → Chủ Nhật) tính vào báo cáo tuần kế tiếp.

**Ngưỡng commit.** Với 15 tuần, Mức 5 của TC2.4 (≥ 90% số tuần có commit) tương
đương **≥ 14/15 tuần**; Mức 4 (≥ 75%) là ≥ 12/15 tuần. Nghỉ quá 2 tuần liên tiếp
là đã rớt khỏi Mức 5, và không có cách nào bù lại.

---

## 3. Hiện trạng so với rubric

Rà soát ngày 10/09/2026, bằng chứng lấy trực tiếp từ repo.

| Tiêu chí | Hiện trạng | Gate | Trần điểm hiện tại |
|---|---|---|---|
| TC2.5 Kiểm thử | 4 file `tests.py` đều là stub 3 dòng, không có `test_*.py` nào | **G5** | 1,75 / 5 |
| TC2.6 CI/CD | Không có `.github/workflows/` | **G6** | 2,75 / 5 |
| TC2.7 Thực nghiệm người dùng | Chưa có | **G7** | 1,75 / 5 |
| TC2.3 Làm chủ AI | ✅ Đã tạo `AI_USAGE_LOG.md` (10/09/2026) — gate G3 đã gỡ | — | cần duy trì mỗi phiên |
| TC2.4 Chất lượng mã | Commit dồn cục ở giai đoạn TLCN (tuần 18/05/2026: 32 commit; tuần 08/06/2026: 21 commit; xen kẽ nhiều tuần trống); 3 merge commit, gần như 1 nhánh | — | khó vượt Mức 3 |
| TC2.4 Bảo mật | ✅ `.env` chưa từng bị commit; quét lịch sử không thấy secret thật | — | đạt ngưỡng Mức 5 |
| TC2.1 Đặc tả | 26 UC chưa có acceptance criteria; NFR chưa định lượng | — | trần Mức 2–3 |
| TC1 Thực tiễn | Chưa khảo sát bên liên quan, chưa chốt KPI nghiệp vụ | — | trần Mức 2 |

**Tổng thiệt hại hiện tại:** ba gate còn lại G5/G6/G7 đang chặn khoảng **8,75 điểm**
trước khi hội đồng đánh giá chất lượng code. (G3 đã gỡ ngày 10/09/2026.)

---

## 4. Backlog

Trạng thái: `Chưa bắt đầu` · `Đang làm` · `Xong` · `Hoãn`

### Giai đoạn 0 — Nền tảng quy trình (Tuần 1–4)

Làm sớm vì đây là loại minh chứng tích lũy theo thời gian, không back-fill được.

| ID | Việc | TC | Trạng thái | Ghi chú |
|---|---|---|---|---|
| P-01 | Khung specs: `AGENTS.md`, `CLAUDE.md`, `docs/` | TC2.4 | **Xong** | 10/09/2026 |
| P-02 | Chốt lịch KLTN | — | **Xong** | 10/09/2026 — xem §2 |
| P-03 | Soạn **bản cam kết sản phẩm + bộ metric**, ký với GVHD | G1, TC1, TC2.2 | Đang làm | Bản nháp: [`COMMITMENT.md`](COMMITMENT.md) (đã có danh sách chức năng, chưa có metric). **Hạn: hết Tuần 7 — 25/10/2026.** Nguồn: rubric Mục 2 Bước 3, Mục 7 G1, Mục 8 hồ sơ số 3. Gồm danh sách chức năng cam kết (mẫu số của TC2.2) + ngưỡng metric (Mục 5 cho phép điều chỉnh tại đây) + ≥ 5 KPI nghiệp vụ (TC1 Mức 5). **Khác đề cương P-08:** rubric không nhắc tới đề cương; bản cam kết là văn bản của Bước 3, phải có metric, có chữ ký SV + GVHD và qua rà soát của bộ môn (đọc lại nguyên văn 16/09/2026). Rubric không quy định hình thức → **hỏi GVHD** nên gộp phần cam kết + metric vào đề cương hay làm văn bản riêng để ký |
| P-04 | Tạo `AI_USAGE_LOG.md`, ghi từ phiên làm việc đầu tiên | G3, TC2.3 | **Xong** | 10/09/2026 — duy trì ghi mỗi phiên có dùng AI |
| P-05 | Duy trì nhịp commit + báo cáo hằng tuần | G2, TC2.4 | Đang làm | Chạy suốt 15 tuần. **Hạn nộp portal: trước 17:00 Thứ Sáu mỗi tuần** (GVHD chốt, áp dụng từ Tuần 2). Tuần 1 đã nộp portal 12/09/2026; Tuần 2 nộp 18/09/2026. Báo cáo tuần không nằm trong repo (D-021) |
| P-06 | Làm việc trên nhánh `develop`, merge vào `main` qua Pull Request (làm một mình) | TC2.4 | Đang làm | Theo D-016 (thay D-012). Đã merge PR #1 → #7 (PR #7 là PR đầu tiên có CI chạy); nhánh `develop` tạo 11/09/2026. Mức 5 cần ≥ 90% thay đổi qua PR có review. Còn lại: ghi cách hiểu "review" vào bản cam kết P-03; bật branch protection cho `main` khi có CI (P-10) |
| P-07 | Tách `SRS.md` thành `SRS.md` (yêu cầu, Mục 1–6) + `SDD.md` (thiết kế, Mục 7–9) | TC2.1 | **Xong** | 11/09/2026. Theo D-011 (thay P-27 cũ). `SRS.md` giữ Mục 1–6 + kiểm thử, hạn chế (đánh số lại 7–9); `SDD.md` nhận Mục 7–9 cũ (thành Mục 1–3). Chỉ chuyển chỗ, chưa sửa nội dung — việc rà soát để cho P-23, P-24. Bảng đối chiếu số mục: §6 dòng 4 |
| P-08 | Nộp đề cương KLTN (`DE_CUONG.md`) để GVHD góp ý nội dung; sửa theo góp ý | — | Đang làm | Theo ý kiến GVHD cho bản nộp Tuần 1. Nộp cùng báo cáo Tuần 2, **hạn 17:00 Thứ Sáu 18/09/2026**. Portal không nhận `.md` ở ô đính kèm → đã xuất DOCX + PDF theo mẫu đề cương TLCN (14/09/2026), **SV đã duyệt 16/09/2026**. Góp ý nhận được sửa thẳng vào `DE_CUONG.md`. Đề cương **không thay** bản cam kết P-03 — xem ghi chú P-03. **21/09/2026:** file chuyển sang `docs/weekly_report/`, không còn trong repo — cùng lý do với báo cáo tuần (D-021) |

### Giai đoạn 1 — Gỡ gate kỹ thuật (Tuần 3–9)

| ID | Việc | TC | Trạng thái | Ghi chú |
|---|---|---|---|---|
| P-10 | Dựng CI: build → lint → test → quét secret → đóng gói → deploy | G6, TC2.6 | Đang làm | Mức 5 cần ≥ 6 chặng. Dựng sớm để kịp tích lũy ≥ 10 lần deploy. **17/09/2026:** theo D-019, tạo `.github/workflows/ci.yml` trên GitHub Actions — job `twin-files` (so `AGENTS.md`/`CLAUDE.md`) và job `test` (cài đặt → `manage.py check` → `makemigrations --check` → `pytest --cov`, Python 3.12). Chặng kiểm tra migration phát hiện model `CartOrder` thiếu migration từ TLCN → thêm migration `0005` (D-020). Còn: thêm chặng lint (P-14), quét secret (P-15), đóng gói image + deploy (P-11); bật branch protection cho `main` |
| P-11 | Dựng hạ tầng KLTN riêng (host + DB + image storage), cập nhật `.env` | TC2.2, TC2.6 | Chưa bắt đầu | Theo D-002. Bổ sung nhóm `VNPAY_*` vào `.env.example` |
| P-12 | Cài pytest + pytest-django, viết test cho luồng cốt lõi | G5, TC2.5 | Đang làm | Ưu tiên: auth, giỏ hàng, checkout, tool AI. **16/09/2026:** dựng hạ tầng test theo D-018 (`settings_test.py`, `pytest.ini`, `conftest.py`, `requirements-dev.txt`); 48 test cho đăng ký/đăng nhập, giỏ hàng, checkout, VNPay, trợ lý AI — 43 xanh, 5 `xfail` tái hiện lỗi L-6 → L-10 (3 lỗi mới L-8, L-9, L-10 phát hiện khi viết test). Còn: `useradmin` (UC-19, UC-20, UC-26), đánh giá (L-3), wishlist, hồ sơ; mỗi AC viết ở P-23 cần test tương ứng |
| P-13 | Báo cáo coverage trong CI | TC2.5 | Đang làm | Mức 5 cần ≥ 70% ở module cốt lõi. Đã cài pytest-cov (D-018). Số đo đầu tiên, chạy tay 16/09/2026: tổng 66%; `core/views.py` 57%, `store_api/views.py` 73%, `userauths/views.py` 71%, `useradmin/views.py` 21%. **17/09/2026:** CI in bảng độ phủ vào trang tóm tắt mỗi lần chạy và lưu `coverage.xml` (D-019). Còn: chốt "module cốt lõi" trong bản cam kết P-03; cân nhắc đặt ngưỡng tối thiểu làm CI đỏ khi đã chốt |
| P-14 | Cấu hình linter + phân tích tĩnh, đưa vào CI | TC2.4 | Chưa bắt đầu | Mức 5 cần 0 lỗi lint, 0 issue Blocker/Critical, trùng lặp ≤ 3% |
| P-15 | Quét secret tự động (gitleaks) trong CI | TC2.4 | Chưa bắt đầu | Hiện đang sạch — cần báo cáo làm minh chứng |
| P-16 | Health check + log tập trung + cảnh báo sau triển khai | TC2.6 | Chưa bắt đầu | Yêu cầu của Mức 5 |
| P-17 | Sửa các lỗi nghiệp vụ và bảo mật đã phát hiện (L-3, L-5 → L-10 trong [`COMMITMENT.md`](COMMITMENT.md) §3) | TC2.2, TC2.5 | Đang làm | Mỗi lỗi có sẵn test tái hiện đánh dấu `xfail` từ P-12; sửa xong thì gỡ `xfail` trong cùng commit. **21/09/2026:** xong L-6 — giá giỏ hàng và tổng đơn đọc từ `Product` thay vì từ tham số trình duyệt, tiền tính bằng `Decimal` (D-022); thêm 3 test cho hành vi mới. Cùng ngày xong L-8 — trang hoàn tất không còn tự đặt đơn thành đã thanh toán, chỉ `vnpay_return` / `vnpay_ipn` làm việc đó (D-023); thêm 2 test. Xong L-7 — `_refresh_cart` hạ số lượng của dòng giỏ xuống bằng tồn kho và bỏ dòng hết hàng (D-024); thêm 5 test. Còn L-9, L-10, L-5, L-3 |

### Giai đoạn 2 — Đặc tả và thực nghiệm (Tuần 6–13)

| ID | Việc | TC | Trạng thái | Ghi chú |
|---|---|---|---|---|
| P-21 | Định lượng hóa NFR (≥ 5 ràng buộc đo được) | TC2.1 | Chưa bắt đầu | VD: thời gian phản hồi, số người dùng đồng thời |
| P-23 | Rà soát đặc tả TLCN trong `SRS.md`: sửa chỗ sai/lỗi thời + viết acceptance criteria cho 26 use case | TC2.1 | Chưa bắt đầu | Gộp P-20 cũ: rà tới use case nào thì viết AC cho use case đó luôn. Mức 5 cần 100% use case có AC. Ghi từng lần sửa vào §6; mỗi AC nên có test tương ứng ở P-12 |
| P-24 | Cập nhật sơ đồ thiết kế trong `SDD.md` cho khớp mã nguồn hiện tại | TC2.1 | Chưa bắt đầu | Hội đồng đối chiếu ngẫu nhiên 5 điểm. Rủi ro lịch: sơ đồ tuần tự tốn thời gian hơn dự tính (phải đọc lại luồng thật trong code rồi mới vẽ được), nên bắt đầu sớm trong Giai đoạn 2 và vẽ dần từng luồng, đừng dồn vào lúc viết quyển báo cáo cuối kỳ |
| P-25 | Thực nghiệm với khoảng 3–5 người dùng thật: phỏng vấn nhu cầu (~5 phút đầu) → làm tác vụ → đo SUS | G7, TC2.7, TC1 | Chưa bắt đầu | Gộp P-22 cũ, theo D-013. Số người theo D-017: theo ngưỡng tham chiếu của rubric, 3–4 người là Mức 3, 5 người là Mức 4 của TC2.7; ngưỡng chính thức chốt ở bản cam kết P-03. Phần phỏng vấn là minh chứng TC1 (≥ 1 người → Mức 3, ≥ 2 → Mức 4, ≥ 3 → Mức 5); phần tác vụ + SUS cho TC2.7. Biên bản ghi tách hai phần. Phải đúng nhóm đối tượng, không chỉ bạn cùng lớp |
| P-26 | Một vòng cải tiến theo phản hồi + đo lại trước–sau | TC2.7 | Chưa bắt đầu | Điều kiện của Mức 5 |

*P-20 (viết AC) đã gộp vào P-23; P-22 (lấy ý kiến bên liên quan) đã gộp vào P-25
— xem D-013; P-27 (tách SRS/SDD) đã chuyển lên Giai đoạn 0 thành P-07 — xem
D-011. Ba mã này không cấp lại cho việc khác.*

### Giai đoạn 3 — Báo cáo và bảo vệ (Tuần 12–15)

| ID | Việc | TC | Trạng thái | Ghi chú |
|---|---|---|---|---|
| P-30 | Viết báo cáo KLTN | TC4 | Chưa bắt đầu | Cần ≥ 5 tài liệu ngoại ngữ chất lượng được vận dụng |
| P-31 | Viết mục "Các hướng phát triển mở rộng" | TC4 | Chưa bắt đầu | Nơi chứa các ý tưởng ngoài phạm vi ở §1 |
| P-32 | Kiểm tra trùng lặp đạo văn (≤ 20%) | TC4 | Chưa bắt đầu | Hồ sơ minh chứng bắt buộc |
| P-33 | Chuẩn bị slide + demo trực tiếp trên môi trường đã triển khai | TC3 | Chưa bắt đầu | Mức 5: demo trực tiếp, không dùng video |
| P-34 | Tổng hợp bộ hồ sơ minh chứng (12 mục theo rubric) | mọi TC | Chưa bắt đầu | Thiếu mục nào thì tiêu chí đó không được xếp từ Mức 4 |

---

## 5. Nhật ký tiến độ

Mỗi tuần thêm một dòng. Bản đầy đủ nằm trên portal (D-021).

| Tuần | Việc chính | Kết quả |
|---|---|---|
| Tuần 1 | Đọc rubric KLTN; rà soát repo so với rubric; dựng khung specs (P-01); chốt lịch (P-02); tạo AI Usage Log (P-04); điều chỉnh backlog | Xác định 4 gate đang vướng; tạo `AGENTS.md`, `CLAUDE.md`, `docs/`; xóa `.github/copilot-instructions.md`; gỡ gate G3; chốt làm theo nhánh + PR (D-012), tách SRS/SDD ngay từ đầu (D-011), gộp khảo sát vào thực nghiệm (D-013); chốt mô hình một nhà bán (D-015); soạn nháp bản cam kết (P-03) và đề cương KLTN; đổi sang làm trên nhánh `develop` (D-016); tách `SRS.md` / `SDD.md` (P-07) |
| Tuần 2 | Ghi nhận hạn nộp Thứ Sáu và ý kiến GVHD Tuần 1; sửa đề cương sang 3–5 người thực nghiệm (D-017), xuất DOCX/PDF (P-08); làm rõ đề cương khác bản cam kết (P-03); soạn `tuan-02.md` | SV duyệt đề cương 16/09; chưa trình bản cam kết, chưa chốt L-2 → L-7, chưa chọn hạ tầng (P-11). Bắt đầu sớm P-12: 48 test tự động (43 xanh, 5 `xfail`), phát hiện L-8 → L-10 (D-018). 17/09: bắt đầu sớm P-10 — CI trên GitHub Actions (D-019); thêm migration còn thiếu từ TLCN (D-020) |
| Tuần 3 | Bắt đầu P-17 — sửa ba lỗ hổng của luồng mua hàng: L-6 (giá giỏ hàng và tổng đơn hàng đọc từ database thay vì từ tham số trình duyệt, D-022), L-8 (chỉ VNPay xác nhận được đơn đã thanh toán, D-023) và L-7 (số lượng không vượt quá tồn kho, D-024) | Gộp bốn vòng lặp cộng tiền trong `core/views.py` thành `_refresh_cart`; tiền tính bằng `Decimal`; test `xfail` của L-6 chuyển xanh và thêm 3 test cho hành vi mới — bộ test còn 47 xanh + 4 `xfail`. `/add-to-cart/` rút còn hai tham số `id` và `qty`; gỡ phần JavaScript gửi giá và bốn `<input type="hidden">` chỉ tồn tại để nuôi nó trong 5 template. Ghi hai ràng buộc nghiệp vụ mới vào `SRS.md` §6.1 (§6 dòng 6). L-8: `payment_completed_view` bỏ đoạn tự đặt `paid_status = True`, đơn online chưa được VNPay xác nhận thì quay về trang thanh toán; thêm 2 test cho hai lối vào hợp lệ của trang hoàn tất — bộ test còn 50 xanh + 3 `xfail`. L-7: `_refresh_cart` đọc thêm `stock_count` nên một chỗ kiểm tra phủ cả ba lối vào (thêm giỏ, sửa số lượng, tạo đơn); `add_to_cart` phải gọi `_refresh_cart` trước khi trả JSON thì số lượng gửi về trang mới là số đã hạ. Đặc tả TLCN viết "báo lỗi và reset", nhưng báo lỗi qua AJAX thì phải sửa cả ba chỗ JavaScript trong `base.html`, nên chọn hạ số lượng và sửa lại câu đặc tả (§6 dòng 8) — bộ test còn 56 xanh + 2 `xfail` |

---

## 6. Nhật ký chỉnh sửa đặc tả

[`SRS.md`](SRS.md) và [`SDD.md`](SDD.md) là tài liệu sống. Đặc tả TLCN có thể sai
hoặc đã lỗi thời so với mã nguồn — khi phát hiện thì sửa file tương ứng và ghi lại
tại đây. Các dòng trước dòng 4 dùng số mục của `SRS.md` trước khi tách; tra số mục
mới ở dòng 4.

Vì sao ghi: hội đồng đối chiếu đặc tả với mã nguồn tại buổi bảo vệ. Một lần sửa có
ghi lý do là minh chứng sinh viên nắm được hệ thống; một đặc tả sai để nguyên vì
"báo cáo cũ viết vậy" thì ngược lại.

| # | Ngày | Mục sửa | Sửa gì | Vì sao | Commit |
|---|---|---|---|---|---|
| 1 | 10/09/2026 | §2.3, §5, §10, §11, §12 | Bỏ cách gọi "baseline đóng băng"; chuyển SRS thành tài liệu sống | Đặc tả TLCN chưa được kiểm chứng lại với mã nguồn hiện tại; giữ nó ở trạng thái bất biến sẽ khóa luôn cả những chỗ sai | *(chưa commit)* |
| 2 | 10/09/2026 | Toàn file | Đổi tên `PRD.md` → `SRS.md`, thêm ghi chú ranh giới SRS/SDD | Rubric Mục 8 gọi tên hồ sơ là "SRS/SDD"; nội dung file vốn là đặc tả yêu cầu chứ không phải PRD — xem D-009 | *(chưa commit)* |
| 3 | 11/09/2026 | §2.1, §2.2, §2.3, §3 (A3), §4.3, FR-A-02, FR-A-06, §6.1 (UC-19), §8 | A3 "Người bán vận hành gian hàng riêng" → "Nhân viên cửa hàng"; thêm mô hình một nhà bán vào phạm vi, marketplace vào ngoài phạm vi. Giữ nguyên §11 (trích nguyên văn TLCN) và mã `FR-V-xx` | Mã nguồn không có vai trò người bán riêng — mọi staff thấy toàn bộ cửa hàng (chỗ lệch L-1 trong `COMMITMENT.md`) — xem D-015 | *(chưa commit)* |
| 4 | 11/09/2026 | Toàn file `SRS.md`; tạo `SDD.md` | Tách đặc tả thiết kế sang `SDD.md`, nội dung giữ nguyên. Số mục: SRS §7 → SDD §1 · SRS §7.1 → SDD §1.1 · SRS §8 → SDD §2 · SRS §9 → SDD §3 · SRS §9.1 → SDD §3.1 · SRS §10 → SRS §7 · SRS §11 → SRS §8 · SRS §12 → SRS §9. Thay ghi chú "sẽ tách" ở đầu `SRS.md` bằng ghi chú ranh giới; thêm ghi chú "nợ thiết kế" ở cuối SDD §3 | P-07, theo D-011: tách trước P-23 và P-24 để mỗi việc chỉ đụng tới một file. Kiểm thử và hạn chế ở lại SRS vì D-011 chỉ chuyển Mục 7–9 | *(chưa commit)* |
| 5 | 16/09/2026 | SRS §7 | Thay ghi chú "chưa có kiểm thử tự động" bằng đối chiếu TC_01 → TC_05 với test tự động; ghi nhận *Kết quả mong đợi* của TC_02, TC_04 không khớp thông báo trong code | Viết test ở P-12 thấy hai câu thông báo mà TLCN ghi PASS không có trong mã nguồn. Chưa sửa cột kết quả vì câu chữ thông báo chốt ở P-23 (acceptance criteria) | `6df5e0f` |
| 6 | 21/09/2026 | SRS §6.1 | Thêm hai ràng buộc nghiệp vụ: giá của dòng giỏ và tổng tiền của đơn do hệ thống tra từ sản phẩm; sản phẩm bị gỡ bán thì dòng đó rời khỏi giỏ | Sửa L-6 (D-022). Ràng buộc thứ nhất trước nay chỉ là ngầm định nên không ai viết ra, và đúng chỗ ngầm định đó thành lỗ hổng. Ràng buộc thứ hai là hành vi mới do cách sửa sinh ra, người dùng nhìn thấy được nên phải có trong đặc tả | `23e91e1` |
| 7 | 21/09/2026 | SRS §6.1 | Thêm hai ràng buộc cho UC-09: đơn online chỉ thành *đã thanh toán* khi VNPay xác nhận chữ ký; mở trang hoàn tất bằng đơn chưa thanh toán thì quay về trang thanh toán | Sửa L-8 (D-023). Ràng buộc thứ nhất là điều kiện mà `payment_completed_view` vi phạm — không viết ra thì không nói được chỗ nào sai. Ràng buộc thứ hai là hành vi mới người dùng nhìn thấy được | `8e22574` |
| 8 | 21/09/2026 | SRS §6.1 | Viết lại ràng buộc tồn kho của UC-06: số lượng vượt tồn kho thì bị *hạ xuống bằng tồn kho và báo cho khách*, thay cho câu cũ "báo lỗi và reset về số lượng hợp lệ"; nói rõ máy chủ kiểm tra ở cả ba lối vào. Thêm ràng buộc: sản phẩm hết hàng thì dòng đó rời khỏi giỏ | Sửa L-7 (D-024). Câu cũ mô tả một hành vi mà giao diện AJAX hiện tại không làm được nếu không sửa JavaScript; hạ số lượng vừa đúng nghiệp vụ vừa hợp với cách trang giỏ hàng đang chạy. Ràng buộc thứ hai là hành vi mới người dùng nhìn thấy được | `219b569` |