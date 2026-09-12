# PLAN — Grocerly (KLTN)

Kế hoạch cải tiến và theo dõi tiến độ. Cập nhật khi trạng thái thay đổi, không
chờ tới cuối kỳ.

| | |
|---|---|
| Cập nhật lần cuối | 11/09/2026 |
| Đặc tả tham chiếu | [`SRS.md`](SRS.md) (yêu cầu), [`SDD.md`](SDD.md) (thiết kế) |
| Quyết định liên quan | [`DECISIONS.md`](DECISIONS.md) — D-005 (thứ tự ưu tiên), D-008 (phạm vi), D-011 (tách SRS/SDD ngay từ đầu), D-016 (làm trên `develop`, merge vào `main` qua PR — thay D-012), D-013 (gộp khảo sát vào thực nghiệm) |

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
Lịch đầy đủ từng tuần: [`weekly_report/README.md`](weekly_report/README.md).

| Mốc | Tuần | Ngày | Ghi chú |
|---|---|---|---|
| Bắt đầu | Tuần 1 | 07/09/2026 – 13/09/2026 | |
| Hết Giai đoạn 0 | Tuần 4 | 28/09/2026 – 04/10/2026 | |
| **Chốt cam kết sản phẩm + bộ metric** | **hết Tuần 7** | **25/10/2026** | **Mốc 50%. Gate G1 — trễ là *không đủ điều kiện bảo vệ*.** |
| Xong thực nghiệm người dùng | Tuần 12 | 23/11/2026 – 29/11/2026 | |
| Hoàn tất báo cáo | Tuần 15 | 14/12/2026 – 20/12/2026 | |
| Phản biện | — | Dự kiến tháng 12/2026 | |

**Nhịp bắt buộc:** báo cáo tiến độ với GVHD ≥ 1 lần/tuần, ghi vào
[`weekly_report/`](weekly_report/). Dưới 0,5 lần/tuần → gate **G2** → TC2.2 và
TC2.4 mỗi tiêu chí bị hạ một mức.

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
| P-03 | Soạn **bản cam kết sản phẩm + bộ metric**, ký với GVHD | G1, TC1, TC2.2 | Đang làm | Bản nháp: [`COMMITMENT.md`](COMMITMENT.md) (đã có danh sách chức năng, chưa có metric). **Hạn: hết Tuần 7 — 25/10/2026.** Nguồn: rubric Mục 2 Bước 3, Mục 7 G1, Mục 8 hồ sơ số 3. Gồm danh sách chức năng cam kết (mẫu số của TC2.2) + ngưỡng metric (Mục 5 cho phép điều chỉnh tại đây) + ≥ 5 KPI nghiệp vụ (TC1 Mức 5) |
| P-04 | Tạo `AI_USAGE_LOG.md`, ghi từ phiên làm việc đầu tiên | G3, TC2.3 | **Xong** | 10/09/2026 — duy trì ghi mỗi phiên có dùng AI |
| P-05 | Duy trì nhịp commit + báo cáo hằng tuần | G2, TC2.4 | Chưa bắt đầu | Chạy suốt 15 tuần |
| P-06 | Làm việc trên nhánh `develop`, merge vào `main` qua Pull Request (làm một mình) | TC2.4 | Đang làm | Theo D-016 (thay D-012). Đã có PR #1, #2, #3; nhánh `develop` tạo 11/09/2026. Mức 5 cần ≥ 90% thay đổi qua PR có review. Còn lại: ghi cách hiểu "review" vào bản cam kết P-03; bật branch protection cho `main` khi có CI (P-10) |
| P-07 | Tách `SRS.md` thành `SRS.md` (yêu cầu, Mục 1–6) + `SDD.md` (thiết kế, Mục 7–9) | TC2.1 | **Xong** | 11/09/2026. Theo D-011 (thay P-27 cũ). `SRS.md` giữ Mục 1–6 + kiểm thử, hạn chế (đánh số lại 7–9); `SDD.md` nhận Mục 7–9 cũ (thành Mục 1–3). Chỉ chuyển chỗ, chưa sửa nội dung — việc rà soát để cho P-23, P-24. Bảng đối chiếu số mục: §6 dòng 4 |

### Giai đoạn 1 — Gỡ gate kỹ thuật (Tuần 3–9)

| ID | Việc | TC | Trạng thái | Ghi chú |
|---|---|---|---|---|
| P-10 | Dựng CI: build → lint → test → quét secret → đóng gói → deploy | G6, TC2.6 | Chưa bắt đầu | Mức 5 cần ≥ 6 chặng. Dựng sớm để kịp tích lũy ≥ 10 lần deploy |
| P-11 | Dựng hạ tầng KLTN riêng (host + DB + image storage), cập nhật `.env` | TC2.2, TC2.6 | Chưa bắt đầu | Theo D-002. Bổ sung nhóm `VNPAY_*` vào `.env.example` |
| P-12 | Cài pytest + pytest-django, viết test cho luồng cốt lõi | G5, TC2.5 | Chưa bắt đầu | Ưu tiên: auth, giỏ hàng, checkout, tool AI |
| P-13 | Báo cáo coverage trong CI | TC2.5 | Chưa bắt đầu | Mức 5 cần ≥ 70% ở module cốt lõi |
| P-14 | Cấu hình linter + phân tích tĩnh, đưa vào CI | TC2.4 | Chưa bắt đầu | Mức 5 cần 0 lỗi lint, 0 issue Blocker/Critical, trùng lặp ≤ 3% |
| P-15 | Quét secret tự động (gitleaks) trong CI | TC2.4 | Chưa bắt đầu | Hiện đang sạch — cần báo cáo làm minh chứng |
| P-16 | Health check + log tập trung + cảnh báo sau triển khai | TC2.6 | Chưa bắt đầu | Yêu cầu của Mức 5 |

### Giai đoạn 2 — Đặc tả và thực nghiệm (Tuần 6–13)

| ID | Việc | TC | Trạng thái | Ghi chú |
|---|---|---|---|---|
| P-21 | Định lượng hóa NFR (≥ 5 ràng buộc đo được) | TC2.1 | Chưa bắt đầu | VD: thời gian phản hồi, số người dùng đồng thời |
| P-23 | Rà soát đặc tả TLCN trong `SRS.md`: sửa chỗ sai/lỗi thời + viết acceptance criteria cho 26 use case | TC2.1 | Chưa bắt đầu | Gộp P-20 cũ: rà tới use case nào thì viết AC cho use case đó luôn. Mức 5 cần 100% use case có AC. Ghi từng lần sửa vào §6; mỗi AC nên có test tương ứng ở P-12 |
| P-24 | Cập nhật sơ đồ thiết kế trong `SDD.md` cho khớp mã nguồn hiện tại | TC2.1 | Chưa bắt đầu | Hội đồng đối chiếu ngẫu nhiên 5 điểm |
| P-25 | Thực nghiệm với ≥ 10 người dùng thật: phỏng vấn nhu cầu (~5 phút đầu) → làm tác vụ → đo SUS | G7, TC2.7, TC1 | Chưa bắt đầu | Gộp P-22 cũ, theo D-013. Phần phỏng vấn là minh chứng TC1 (≥ 1 người → Mức 3, ≥ 2 → Mức 4, ≥ 3 → Mức 5); phần tác vụ + SUS cho TC2.7. Biên bản ghi tách hai phần. Phải đúng nhóm đối tượng, không chỉ bạn cùng lớp |
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

Mỗi tuần thêm một dòng. Chi tiết đặt trong [`weekly_report/`](weekly_report/).

| Tuần | Việc chính | Kết quả |
|---|---|---|
| Tuần 1 | Đọc rubric KLTN; rà soát repo so với rubric; dựng khung specs (P-01); chốt lịch (P-02); tạo AI Usage Log (P-04); điều chỉnh backlog | Xác định 4 gate đang vướng; tạo `AGENTS.md`, `CLAUDE.md`, `docs/`; xóa `.github/copilot-instructions.md`; gỡ gate G3; chốt làm theo nhánh + PR (D-012), tách SRS/SDD ngay từ đầu (D-011), gộp khảo sát vào thực nghiệm (D-013); chốt mô hình một nhà bán (D-015); soạn nháp bản cam kết (P-03) và đề cương KLTN; đổi sang làm trên nhánh `develop` (D-016); tách `SRS.md` / `SDD.md` (P-07) |

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