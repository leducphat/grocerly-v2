# Báo cáo tiến độ — Tuần 02 / 15

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| Kỳ báo cáo | **Tuần 2**: 14/09/2026 → 20/09/2026 |
| Nộp portal | DD/09/2026 — hạn **17:00 Thứ Sáu 18/09/2026** |

> Tra số tuần và khoảng ngày tương ứng ở [`README.md`](README.md).

> **⚠️ BẢN NHÁP — số liệu tính tới 16/09/2026.** Cập nhật Mục 1, 2 và 6 nếu có
> thêm việc trước lúc nộp; điền ngày nộp và số PR sau khi merge `develop` → `main`.

**Tóm tắt.** Tuần 2 tiếp tục Giai đoạn 0, vẫn chưa đụng tới mã nguồn ứng dụng.
Việc chính là hoàn thiện **đề cương KLTN** theo yêu cầu của GVHD ở bản nộp Tuần 1:
sửa số người dùng thực nghiệm thành khoảng 3–5 người (D-017), xuất bản DOCX/PDF theo
mẫu đề cương TLCN, sinh viên đã duyệt để nộp kèm báo cáo này. Đọc lại rubric cho thấy
đề cương **không thay** được bản cam kết sản phẩm + metric (Bước 3, gate G1) — hai
văn bản khác nhau, bản cam kết vẫn phải ký trước 25/10/2026.

---

## 1. Đã làm trong tuần

| ID | Việc | Kết quả | Minh chứng |
|---|---|---|---|
| P-05 | Ghi nhận hạn nộp báo cáo tuần (17:00 Thứ Sáu) và ý kiến GVHD cho bản nộp Tuần 1 | **Xong.** Thêm lịch hạn nộp 15 tuần vào [`README.md`](README.md); ghi ý kiến GVHD cuối [`tuan-01.md`](tuan-01.md); thêm việc P-08 | commit `9e8dd3e` |
| P-08 | Hoàn thiện đề cương KLTN ([`DE_CUONG.md`](../DE_CUONG.md)) để nộp GVHD góp ý | **Xong bản nộp.** Sửa số người thực nghiệm thành khoảng 3–5 người; xuất DOCX + PDF (7 trang) theo trình bày trang đề cương của báo cáo TLCN, vì portal không nhận `.md`. SV duyệt 16/09/2026 | commit `9e8dd3e` · file đính kèm trên portal |
| — | Chốt số người dùng thực nghiệm (D-017) | **Xong.** Khoảng 3–5 người — theo ngưỡng tham chiếu của rubric là Mức 3–4 của TC2.7; ngưỡng chính thức chốt ở bản cam kết. Đính chính D-013 (đã ghi nhầm "bắt buộc ≥ 10 người") | commit `9e8dd3e` — [`DECISIONS.md`](../DECISIONS.md) D-017 |
| P-03 | Làm rõ quan hệ giữa đề cương và bản cam kết sản phẩm | **Xong phần làm rõ.** Rubric không nhắc tới đề cương; bản cam kết là hồ sơ của Mục 2 Bước 3: phải có metric, có chữ ký SV + GVHD, bộ môn rà soát. Ghi vào [`PLAN.md`](../PLAN.md) P-03. Phần metric (§5 của bản cam kết) **chưa soạn** | `PLAN.md` P-03, P-08 *(chưa commit)* |

## 2. Chỉ số trong tuần

| Chỉ số | Giá trị |
|---|---|
| Số commit | 2 tính tới 16/09/2026 (`9e8dd3e`, `560bdf0`), toàn bộ là tài liệu |
| Số Pull Request đã merge (có review) | 0 tính tới 16/09/2026 — PR `develop` → `main` sẽ mở trước lúc nộp |
| Số lần CI chạy / tỉ lệ build xanh | 0 — chưa có CI (P-10) |
| Số lần deploy | 0 — chưa có hạ tầng KLTN (P-11) |
| Độ phủ test | 0% — chưa có test tự động (P-12) |
| Số defect còn tồn (Critical/Blocker) | 1 Critical — **L-6** (giá sản phẩm do trình duyệt gửi lên), chưa sửa. Ngoài ra L-3, L-5, L-7 chưa phân mức |

## 3. Vướng mắc

- **Chưa rõ hình thức bản cam kết.** Rubric chỉ yêu cầu "thống nhất bằng văn bản"
  sản phẩm cuối cùng + bộ metric, có chữ ký SV và GVHD, trước mốc 50%; không quy
  định mẫu. Chưa biết GVHD muốn gộp phần này vào đề cương (dưới dạng phụ lục) hay
  làm văn bản riêng, và khoa có biểu mẫu riêng hay không.
- **Kế hoạch Tuần 2 làm chưa hết.** Chưa trình bản cam kết, chưa chốt 6 chỗ lệch
  L-2 → L-7, chưa chọn hạ tầng KLTN (P-11). Tuần này ưu tiên đề cương vì GVHD yêu
  cầu nộp cùng báo cáo; ba việc trên chuyển sang Tuần 3.
- **Vẫn chưa có hạ tầng riêng cho KLTN** — như Tuần 1: `.env` còn trỏ tới
  production của TLCN nên chưa deploy được (D-002).

## 4. Kế hoạch tuần tới

**Tuần 3**: 21/09/2026 → 27/09/2026.

| ID | Việc dự kiến | Mục tiêu hoàn thành |
|---|---|---|
| P-08 | Sửa đề cương theo góp ý của GVHD (nếu có) | Góp ý ghi vào `tuan-03.md`, sửa thẳng `DE_CUONG.md` |
| P-03 | Hỏi GVHD hình thức bản cam kết; chốt L-2 → L-7; soạn nháp §5 metric kỹ thuật + ≥ 5 KPI nghiệp vụ | Có bản nháp §5 đủ mọi tiêu chí TC2.x |
| P-12 | Cài pytest + pytest-django; viết những test đầu tiên cho luồng auth / giỏ hàng | Test chạy được bằng một lệnh, có số coverage đầu tiên |
| P-10 | Dựng CI tối thiểu trên GitHub Actions (cài đặt → kiểm tra → chạy test) | Có lần chạy CI đầu tiên trên `develop` |
| P-11 | Chọn host, database, image storage cho KLTN | Ghi thành quyết định trong `DECISIONS.md` |
| P-05 | Giữ nhịp commit và báo cáo tuần | Nộp `tuan-03.md` trước 17:00 Thứ Sáu 25/09/2026 |

## 5. Ghi chú

**Quyết định mới** — [`../DECISIONS.md`](../DECISIONS.md):

| Mã | Nội dung |
|---|---|
| D-017 | Thực nghiệm với khoảng 3–5 người dùng thật; chấp nhận rủi ro không đạt Mức 5 của TC2.7 (cần ≥ 10 người). Kèm ghi chú đính chính dưới D-013 |

**Chỉnh sửa đặc tả** — không có lần sửa `SRS.md` / `SDD.md` nào trong tuần.

**Điều chỉnh kế hoạch** — thêm P-08 (nộp đề cương theo yêu cầu GVHD); ghi rõ ở
P-03 rằng đề cương không thay bản cam kết; chuyển P-11 và phần chốt L-2 → L-7 của
P-03 sang Tuần 3.

## 6. Bản tóm tắt nộp portal (ô *Nội dung*)

Portal **không nhận file `.md`** ở ô đính kèm, nên bản đầy đủ chỉ tới được GVHD
qua link repo. Chép phần **giữa hai đường kẻ** dưới đây vào ô *Nội dung (hỗ trợ
Markdown)*; nộp sau khi `develop` đã merge vào `main` để link trỏ đúng nội dung,
và **trước 17:00 Thứ Sáu** của tuần báo cáo. Đính kèm file đề cương DOCX/PDF.

---

**Báo cáo tuần 2 (14/09 – 20/09/2026) — Grocerly (KLTN)**

**Sinh viên:** Lê Đức Phát — 21139083 · **GVHD:** Hoàng Văn Dũng
**Repository:** https://github.com/leducphat/grocerly-v2
**Báo cáo đầy đủ:** https://github.com/leducphat/grocerly-v2/blob/main/docs/weekly_report/tuan-02.md

Tuần 2 hoàn thiện đề cương KLTN theo yêu cầu của thầy ở bản nộp Tuần 1; đề cương
được đính kèm để thầy góp ý nội dung. Chưa đụng tới mã nguồn ứng dụng. Em cũng đọc
lại rubric và xác định đề cương không thay được bản cam kết sản phẩm + metric
(Bước 3) — văn bản này vẫn phải ký trước 25/10/2026.

**Đã làm**

- **P-08** — hoàn thiện đề cương KLTN: sửa số người dùng thực nghiệm thành khoảng
  3–5 người, xuất DOCX/PDF theo mẫu đề cương TLCN (commit `9e8dd3e`).
- **D-017** — chốt thực nghiệm với khoảng 3–5 người dùng; đính chính D-013 đã ghi
  nhầm "bắt buộc ≥ 10 người".
- **P-05** — ghi nhận hạn nộp báo cáo trước 17:00 Thứ Sáu và ý kiến của thầy cho
  Tuần 1.
- **P-03** — làm rõ khác biệt giữa đề cương và bản cam kết; phần metric chưa soạn.

**Chỉ số**

- 2 commit, 0 Pull Request đã merge (tính tới 16/09/2026).
- CI: chưa có · Số lần deploy: 0 · Độ phủ test: 0%.
- Defect Critical còn tồn: 1 — giá sản phẩm do trình duyệt gửi lên (chưa sửa).

**Vướng mắc**

- Em xin ý kiến thầy về hình thức bản cam kết sản phẩm + metric: gộp vào đề cương
  dưới dạng phụ lục hay làm văn bản riêng để ký; khoa có biểu mẫu riêng không.
- Kế hoạch Tuần 2 còn dở: chưa chốt 6 chỗ lệch giữa đặc tả và mã nguồn, chưa chọn
  hạ tầng riêng cho KLTN — chuyển sang Tuần 3.

**Kế hoạch tuần 3 (21/09 – 27/09/2026)**

- Sửa đề cương theo góp ý của thầy; soạn nháp phần metric và KPI của bản cam kết.
- Cài pytest, viết những test tự động đầu tiên; dựng CI tối thiểu trên GitHub Actions.
- Chọn hạ tầng riêng cho KLTN (host, database, lưu trữ ảnh).

---

## 7. Khai báo sử dụng AI (điền lên portal)

Tóm tắt từ [`../AI_USAGE_LOG.md`](../AI_USAGE_LOG.md) §1, các phiên 14/09 → 16/09/2026;
ba ô dưới đây chép thẳng vào form khai báo công cụ AI trên portal.

**Công cụ AI:** Claude (qua Claude Code) — **Phiên bản / model:** Opus 5

**Prompt đã dùng**

```
- Ghi nhận hạn nộp báo cáo tuần trước 17:00 Thứ Sáu; ghi ý kiến GVHD cho bản
  Tuần 1: lần sau nộp đề cương để góp ý nội dung.
- So sánh xuất DOCX với PDF xem cái nào giống bản đề cương TLCN nhất; cài pandoc
  rồi làm các bước đã đề xuất.
- Sửa đề cương: số người dùng thực nghiệm thành khoảng 3–5 người; giữ chữ
  "chuyên ngành".
- Theo PLAN thì việc kế tiếp nên làm là gì.
- Tra lại rubric xem bản cam kết sản phẩm có phải là đề cương không.
- Cập nhật PLAN (đề cương đã duyệt, câu hỏi về hình thức bản cam kết); soạn nháp
  báo cáo Tuần 2.
```

**Nội dung AI tạo ra**

```
Chỉ có tài liệu — không có dòng mã nguồn ứng dụng nào:
- Sửa docs/weekly_report/README.md (lịch hạn nộp), tuan-01.md (ý kiến GVHD),
  _TEMPLATE.md, AGENTS.md/CLAUDE.md §2, DE_CUONG.md (số người thực nghiệm),
  PLAN.md (P-03, P-05, P-08, P-25), DECISIONS.md (D-017, đính chính D-013).
- Script xuất đề cương sang DOCX/PDF (pandoc + bộ lọc Lua + LibreOffice) và hai
  file xuất; công cụ này đang ở thư mục tạm, chưa đưa vào repo.
- Bản nháp báo cáo này (tuan-02.md).
AI đọc nguyên văn rubric (Mục 2, Mục 5, Mục 7, TC2.7) để trích dẫn, không tự đặt
ngưỡng.
```

**Phần bạn đã sửa / hoàn thiện**

```
- Cung cấp hạn nộp và ý kiến GVHD; cung cấp báo cáo TLCN làm mẫu trình bày đề cương.
- Chốt khoảng 3–5 người dùng thực nghiệm và sửa lý do trong D-017: 3–5 người là con
  số làm được, 10 người là quá sức — ghi là rủi ro chấp nhận.
- Đọc và duyệt bản DOCX/PDF của đề cương trước khi nộp.
- Hỏi lại quan hệ giữa đề cương và bản cam kết, dẫn tới việc tách rõ hai văn bản
  trong PLAN.
- Lỗi của AI trong tuần (AI_USAGE_LOG mục 2, #14–#17): 3 lỗi trình bày trong công cụ
  xuất đề cương (AI tự phát hiện khi so với trang TLCN) và D-013 ghi nhầm "bắt buộc
  ≥ 10 người" (AI phát hiện khi đọc lại rubric theo yêu cầu đổi số người của SV).
```

---

*Ý kiến GVHD:*
