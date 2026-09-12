# Báo cáo tiến độ — Tuần 01 / 15

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| Kỳ báo cáo | **Tuần 1**: 07/09/2026 → 13/09/2026 |

> Tra số tuần và khoảng ngày tương ứng ở [`README.md`](README.md).

**Tóm tắt.** Tuần đầu tập trung vào *nền tảng quy trình* (Giai đoạn 0): đọc rubric
KLTN, rà soát repo so với rubric, dựng bộ tài liệu đặc tả trong `docs/`, soạn nháp
bản cam kết sản phẩm và đề cương. Chưa đụng tới mã nguồn. Rà soát cho thấy đồ án
đang vướng ba gate chặn điểm là **G5** (chưa có test tự động), **G6** (chưa có
CI/CD) và **G7** (chưa có thực nghiệm người dùng). Gate G3 (thiếu nhật ký dùng AI)
đã gỡ ngay trong tuần.

---

## 1. Đã làm trong tuần

| ID | Việc | Kết quả | Minh chứng |
|---|---|---|---|
| P-01 | Dựng khung specs: `AGENTS.md`, `CLAUDE.md`, `docs/` (SRS, PLAN, DECISIONS, weekly_report) | **Xong.** Xóa `.github/copilot-instructions.md` vì đã sai nhiều chỗ so với code | commit `1ad9305`, `43c1a0a` · PR #1 |
| P-02 | Chốt lịch KLTN 15 tuần | **Xong.** Mốc 50% (hạn ký cam kết) là 25/10/2026 | `PLAN.md` §2, `weekly_report/README.md` — commit `1ad9305` |
| P-04 | Tạo `AI_USAGE_LOG.md`, ghi từ phiên đầu tiên | **Xong.** Gỡ gate G3. Đã ghi 11 lỗi/ảo giác của AI kèm phân tích nguyên nhân (Mức 5 cần ≥ 5) | commit `1ad9305`, `3376284` |
| — | Đưa thư mục công cụ agent `.claude/` ra khỏi repo (D-014) | **Xong** | commit `bbd1595`, `3376284` · PR #1 |
| — | Chốt mô hình **một nhà bán** (D-015): A3 là nhân viên cửa hàng, không phải người bán có gian hàng riêng | **Xong.** Sửa `SRS.md` và `README.md` cho khớp mã nguồn (chỗ lệch L-1) | commit `f002519` · PR #2 |
| P-03 | Soạn **bản cam kết sản phẩm + bộ metric** | **Đang làm.** Nháp [`COMMITMENT.md`](../COMMITMENT.md): 30 chức năng (24 `Có`, 6 `Lệch`) đối chiếu với route/view trong code; 7 chỗ lệch L-1 → L-7 giữa đặc tả TLCN và code. Chưa soạn metric/KPI | commit `f7e3158` · PR #2 |
| — | Soạn đề cương KLTN theo khung đề cương TLCN | **Xong bản nháp** — [`DE_CUONG.md`](../DE_CUONG.md), chờ GVHD góp ý | commit `876df38` · PR #2 |
| P-06 | Chuyển sang làm trên nhánh `develop`, merge vào `main` qua PR (D-016, thay D-012) | **Đang làm.** Đã tạo `develop`; còn ghi cách hiểu "review" vào P-03 và bật branch protection khi có CI | commit `87c1a2a` · PR #3 |
| P-07 | Tách `SRS.md` thành `SRS.md` (yêu cầu) + `SDD.md` (thiết kế) theo D-011 | **Xong.** Chỉ chuyển chỗ Mục 7–9 sang [`SDD.md`](../SDD.md), nội dung giữ nguyên; bảng đối chiếu số mục cũ → mới ghi ở `PLAN.md` §6 dòng 4 | commit `0af7a42` |

## 2. Chỉ số trong tuần

| Chỉ số | Giá trị |
|---|---|
| Số commit | 10 tính tới 12/09/2026 (không tính 3 merge commit), toàn bộ là tài liệu |
| Số Pull Request đã merge (có review) | 3 — PR #1, #2, #3. Tự review theo checklist; cách hiểu "review" cho đồ án một người chưa được GVHD xác nhận |
| Số lần CI chạy / tỉ lệ build xanh | 0 — chưa có CI (P-10) |
| Số lần deploy | 0 — chưa có hạ tầng KLTN (P-11) |
| Độ phủ test | 0% — chưa có test tự động nào (P-12) |
| Số defect còn tồn (Critical/Blocker) | 1 Critical — **L-6**: giá sản phẩm do trình duyệt gửi lên, khách sửa tham số là đặt được hàng với giá tùy ý. Ngoài ra còn 3 lỗi nghiệp vụ chưa phân mức: L-3, L-5, L-7 |

## 3. Vướng mắc

- **Chưa có hạ tầng riêng cho KLTN.** `grocerly/.env` vẫn trỏ tới host, database
  và Cloudinary production của TLCN, nên chưa chạy được `migrate` hay deploy mà
  không đụng vào dữ liệu bài đã chấm (D-002). Phải dựng hạ tầng mới (P-11) trước
  khi có thể deploy và tích lũy số lần deploy mà rubric đếm.
- **Sáu chỗ lệch L-2 → L-7 chưa chốt.** Mỗi chỗ có hai hướng: sửa đặc tả cho khớp
  code, hoặc sửa code cho khớp đặc tả. Hướng nào cũng làm thay đổi danh sách chức
  năng cam kết — mà danh sách này là mẫu số của TC2.2 — nên cần chốt trước khi ký.
- **Chưa có mẫu bản cam kết chính thức.** Bản nháp đang soạn theo rubric Mục 2
  Bước 3 và Mục 5; chưa biết khoa có biểu mẫu riêng hay không.

## 4. Kế hoạch tuần tới

**Tuần 2**: 14/09/2026 → 20/09/2026.

| ID | Việc dự kiến | Mục tiêu hoàn thành |
|---|---|---|
| P-03 | Trình GVHD bản nháp cam kết; chốt L-2 → L-7; bắt đầu soạn §5 (metric kỹ thuật + ≥ 5 KPI nghiệp vụ) | Chốt xong danh sách chức năng và các chỗ lệch; có bản nháp §5 |
| P-06 | Mở PR `develop` → `main` gồm P-07 và báo cáo tuần này | PR được merge trong tuần |
| P-11 | Chọn nhà cung cấp host, database, image storage cho KLTN; bổ sung nhóm `VNPAY_*` vào `.env.example` | Chốt được phương án hạ tầng, ghi thành quyết định trong `DECISIONS.md` |
| P-05 | Giữ nhịp commit và báo cáo tuần | Có commit trong Tuần 2; nộp `tuan-02.md` |

## 5. Cần GVHD hỗ trợ / quyết định

- Duyệt danh sách **30 chức năng cam kết** ([`COMMITMENT.md`](../COMMITMENT.md) §2)
  và cho ý kiến về hướng xử lý các chỗ lệch **L-2 → L-7** (§3).
- Xác nhận cách hiểu **"Pull Request có review"** cho đồ án một người: CI xanh +
  checklist tự review + một lượt review bằng AI đăng thành comment (D-016). Rubric
  TC2.4 Mức 5 đòi ≥ 90% thay đổi qua PR có review.
- Xác nhận việc **gộp khảo sát bên liên quan vào buổi thực nghiệm người dùng**
  (D-013): mỗi buổi dành ~5 phút đầu phỏng vấn nhu cầu, sau đó mới làm tác vụ và
  đo SUS.
- Góp ý **đề cương KLTN** ([`DE_CUONG.md`](../DE_CUONG.md)).
- Cho biết khoa có **biểu mẫu bản cam kết** riêng không.

## 6. Ghi chú

**Quyết định mới** — ghi tại [`../DECISIONS.md`](../DECISIONS.md), D-001 → D-016.
Những quyết định chính:

| Mã | Nội dung |
|---|---|
| D-001 | Áp dụng Spec Driven Development: đặc tả, kế hoạch, quyết định nằm trong `docs/` cùng repo |
| D-002 | Tách hoàn toàn hạ tầng KLTN khỏi hạ tầng TLCN |
| D-005, D-008 | Ưu tiên gỡ gate chặn điểm (test, CI, thực nghiệm); không mở rộng tính năng mới |
| D-007 | `SRS.md` là tài liệu sống — sửa được, mọi lần sửa ghi vào `PLAN.md` §6 |
| D-011 | Tách SRS/SDD ngay từ đầu (thực hiện ở P-07 tuần này) |
| D-013 | Gộp khảo sát bên liên quan vào thực nghiệm người dùng |
| D-015 | Mô hình một nhà bán |
| D-016 | Làm trên nhánh `develop`, merge vào `main` qua PR |

Bốn quyết định đã bị thay thế ngay trong tuần (D-003 → D-006, D-004 → D-007,
D-010 → D-011, D-012 → D-016). Các quyết định cũ được giữ nguyên, chỉ đánh dấu bị
thay thế, để lịch sử thay đổi quyết định vẫn là minh chứng.

**Chỉnh sửa đặc tả** — 4 lần, ghi tại [`../PLAN.md`](../PLAN.md) §6: chuyển SRS
thành tài liệu sống; đổi tên `PRD.md` → `SRS.md`; sửa A3 theo mô hình một nhà bán;
tách `SDD.md`.

**Điều chỉnh kế hoạch** — gộp P-20 (viết acceptance criteria) vào P-23; gộp P-22
(khảo sát) vào P-25; bỏ P-27, đưa việc tách SRS/SDD lên Giai đoạn 0 thành P-07.

---

*Ý kiến GVHD:*
