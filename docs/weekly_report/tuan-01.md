# Báo cáo tiến độ — Tuần 01 / 15

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| Kỳ báo cáo | **Tuần 1**: 07/09/2026 → 13/09/2026 |
| Nộp portal | 12/09/2026 — projects-fit.hcmute.edu.vn |

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
| Số commit | 12 tính tới 12/09/2026 (không tính 4 merge commit), toàn bộ là tài liệu |
| Số Pull Request đã merge (có review) | 4 — PR #1, #2, #3, #4. Tự review theo checklist; cách hiểu "review" cho đồ án một người chưa được GVHD xác nhận |
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

## 5. Ghi chú

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

## 6. Bản tóm tắt nộp portal (ô *Nội dung*)

Portal **không nhận file `.md`** ở ô đính kèm, nên bản đầy đủ chỉ tới được GVHD
qua link repo. Chép phần **giữa hai đường kẻ** dưới đây vào ô *Nội dung (hỗ trợ
Markdown)*; nộp sau khi `develop` đã merge vào `main` để link trỏ đúng nội dung.

---

**Báo cáo tuần 1 (07/09 – 13/09/2026) — Grocerly (KLTN)**

**Sinh viên:** Lê Đức Phát — 21139083 · **GVHD:** Hoàng Văn Dũng
**Repository:** https://github.com/leducphat/grocerly-v2
**Báo cáo đầy đủ:** https://github.com/leducphat/grocerly-v2/blob/main/docs/weekly_report/tuan-01.md

Tuần đầu làm nền tảng quy trình, chưa đụng tới mã nguồn ứng dụng. Rà soát repo theo
rubric cho thấy đồ án đang vướng ba gate G5 (chưa có kiểm thử tự động), G6 (chưa có
CI/CD) và G7 (chưa có thực nghiệm người dùng); gate G3 (thiếu nhật ký dùng AI) đã gỡ
trong tuần.

**Đã làm**

- **P-01** — dựng bộ tài liệu đặc tả trong `docs/` và hai file hướng dẫn agent; xóa file
  hướng dẫn Copilot đã lỗi thời (commit `1ad9305`, `43c1a0a`, PR #1).
- **P-02** — chốt lịch 15 tuần, mốc ký cam kết sản phẩm là 25/10/2026.
- **P-04** — lập nhật ký sử dụng AI, gỡ gate G3; đã ghi 11 lỗi của AI kèm phân tích
  nguyên nhân.
- **P-03 (đang làm)** — nháp bản cam kết: 30 chức năng đối chiếu với mã nguồn, phát hiện
  7 chỗ lệch giữa đặc tả TLCN và code (commit `f7e3158`, PR #2).
- **D-015** — chốt mô hình một nhà bán, sửa đặc tả cho khớp mã nguồn (commit `f002519`).
- **D-016 / P-06** — chuyển sang làm trên nhánh `develop`, vào `main` qua Pull Request.
- **P-07** — tách đặc tả thành `SRS.md` (yêu cầu) và `SDD.md` (thiết kế) theo D-011
  (commit `0af7a42`, PR #4).
- Soạn đề cương KLTN (`DE_CUONG.md`) — chờ GVHD góp ý.

**Chỉ số**

- 12 commit (không tính 4 merge commit), 4 Pull Request đã merge.
- CI: chưa có · Số lần deploy: 0 · Độ phủ test: 0%.
- Defect Critical còn tồn: 1 — giá sản phẩm do trình duyệt gửi lên, khách sửa tham số là
  đặt được hàng với giá tùy ý.

**Vướng mắc**

- Chưa có hạ tầng riêng cho KLTN; cấu hình vẫn trỏ tới production của TLCN nên chưa
  deploy được.
- Sáu chỗ lệch giữa đặc tả và mã nguồn chưa chốt hướng xử lý (sửa đặc tả hay sửa code) —
  việc này quyết định danh sách chức năng đem ký cam kết.
- Chưa rõ khoa có biểu mẫu bản cam kết riêng hay không.

**Kế hoạch tuần 2 (14/09 – 20/09/2026)**

- Trình GVHD bản cam kết, chốt các chỗ lệch, soạn metric và KPI.
- Chọn hạ tầng riêng cho KLTN (host, database, lưu trữ ảnh).
- Giữ nhịp commit và mở PR `develop` → `main` trong tuần.

---

## 7. Khai báo sử dụng AI (điền lên portal)

Ba ô dưới đây tóm tắt từ [`../AI_USAGE_LOG.md`](../AI_USAGE_LOG.md) §1, chép
thẳng vào form khai báo công cụ AI trên portal.

**Công cụ AI:** Claude (qua Claude Code) — **Phiên bản / model:** Opus 5

**Prompt đã dùng**

```
- Đọc repo, báo cáo TLCN và rubric KLTN; dựng CLAUDE.md, AGENTS.md và docs/
  (SRS, PLAN, DECISIONS, AI_USAGE_LOG, weekly_report) theo Spec Driven Development.
- Rà soát backlog: đổi P-01 thành Khung specs, tra rubric xem P-03 là gì, xét đồ án
  một người có cần nhánh + PR, gộp việc viết acceptance criteria vào rà soát đặc tả,
  tách SRS/SDD ngay từ đầu, gộp khảo sát vào thực nghiệm người dùng.
- Tạo nhánh đặt tên đúng convention để commit, push rồi mở PR; đưa .claude/ vào
  .gitignore.
- Soạn nháp bản cam kết các chức năng của Grocerly, đối chiếu với mã nguồn.
- Bỏ gợi ý sản phẩm nổi bật khỏi CN-17; giữ mô hình một nhà bán.
- Giải thích get_bestsellers làm gì và tính thế nào; tạm gỡ công cụ này.
- Viết đề cương KLTN theo khung đề cương TLCN.
- Chuyển sang làm trên nhánh develop, merge vào main qua Pull Request.
- Tách SRS.md thành SRS.md + SDD.md (P-07); viết báo cáo Tuần 1; commit, push,
  mở PR rồi merge vào main.
```

**Nội dung AI tạo ra**

```
Toàn bộ văn bản của bộ tài liệu trong Tuần 1 — không có dòng mã nguồn ứng dụng nào:
- AGENTS.md và CLAUDE.md (hai bản song sinh).
- docs/SRS.md, docs/SDD.md, docs/PLAN.md, docs/DECISIONS.md (D-001 đến D-016),
  docs/COMMITMENT.md, docs/DE_CUONG.md, docs/AI_USAGE_LOG.md,
  docs/weekly_report/README.md, _TEMPLATE.md và tuan-01.md.
- Sửa .gitignore để bỏ qua .claude/; xóa .github/copilot-instructions.md đã lỗi thời.
- Nội dung commit message và mô tả 4 Pull Request.
Để đối chiếu, AI đọc mã nguồn (urls.py, core/views.py, useradmin/views.py,
store_api/views.py), báo cáo TLCN và rubric, thay vì tự đặt ra số liệu.
```

**Phần bạn đã sửa / hoàn thiện**

```
- Bác bỏ 4 phương án AI đề xuất và thay bằng quyết định khác: CLAUDE.md phải tự đứng
  vững (D-006 thay D-003), đặc tả là tài liệu sống chứ không đóng băng (D-007 thay
  D-004), tách SRS/SDD ngay từ đầu (D-011 thay D-010), làm trên nhánh develop thay vì
  mỗi việc một nhánh (D-016 thay D-012).
- Chốt mô hình một nhà bán sau khi đối chiếu với mã nguồn (D-015); bỏ "gợi ý sản phẩm
  nổi bật" khỏi danh sách chức năng cam kết.
- Quyết định không commit bộ công cụ agent vào repo (D-014).
- Quyết định giữ lại công cụ get_bestsellers sau khi AI đã gỡ, và hoàn nguyên thay đổi đó.
- Phát hiện 7 trong 11 lỗi của AI ghi ở AI_USAGE_LOG mục 2 (viết tài liệu sai ngôn ngữ,
  đặt tên PRD thay vì SRS, dùng "SDD" cho hai nghĩa khác nhau, ghi sai hiện trạng chức
  năng so với code) và yêu cầu sửa.
- Bỏ ô "Hình thức trao đổi với GVHD" khỏi mẫu báo cáo tuần; yêu cầu ghi prompt trong
  nhật ký AI ở dạng câu lệnh ngắn.
- Đọc và duyệt từng file trước khi commit; tự review rồi merge 4 Pull Request.
Ghi chú trung thực: Tuần 1 sinh viên chưa tự gõ lại nội dung tài liệu nào; phần đóng góp
nằm ở việc định hướng, bác bỏ đề xuất sai và kiểm soát đầu ra.
```

---

*Ý kiến GVHD:*
