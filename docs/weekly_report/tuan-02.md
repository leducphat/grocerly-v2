# Báo cáo tiến độ — Tuần 02 / 15

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| Kỳ báo cáo | **Tuần 2**: 14/09/2026 → 20/09/2026 |
| Nộp portal | DD/09/2026 — hạn **17:00 Thứ Sáu 18/09/2026** |

> Tra số tuần và khoảng ngày tương ứng ở [`README.md`](README.md).

> **⚠️ BẢN NHÁP — số liệu tính tới 16/09/2026.** Cập nhật Mục 1, 2 và 6 nếu có
> thêm việc trước lúc nộp; điền ngày nộp, số commit và số PR sau khi merge
> `develop` → `main`.

**Tóm tắt.** Tuần 2 hoàn thiện **đề cương KLTN** theo yêu cầu của GVHD ở bản nộp
Tuần 1: sửa số người dùng thực nghiệm thành khoảng 3–5 người (D-017), xuất bản
DOCX/PDF theo mẫu đề cương TLCN, sinh viên đã duyệt để nộp kèm báo cáo này. Đọc lại
rubric cho thấy đề cương **không thay** được bản cam kết sản phẩm + metric (Bước 3,
gate G1) — bản cam kết vẫn phải ký trước 25/10/2026. Ngoài kế hoạch, tuần này bắt
đầu sớm **kiểm thử tự động** (P-12, D-018): 48 test cho đăng ký/đăng nhập, giỏ
hàng, checkout, VNPay và trợ lý AI. Chưa sửa mã nguồn ứng dụng. Viết test phát hiện
thêm 3 lỗi, trong đó **L-8** là lỗi thanh toán nghiêm trọng.

---

## 1. Đã làm trong tuần

| ID | Việc | Kết quả | Minh chứng |
|---|---|---|---|
| P-05 | Ghi nhận hạn nộp báo cáo tuần (17:00 Thứ Sáu) và ý kiến GVHD cho bản nộp Tuần 1 | **Xong.** Thêm lịch hạn nộp 15 tuần vào [`README.md`](README.md); ghi ý kiến GVHD cuối [`tuan-01.md`](tuan-01.md); thêm việc P-08 | commit `9e8dd3e` |
| P-08 | Hoàn thiện đề cương KLTN ([`DE_CUONG.md`](../DE_CUONG.md)) để nộp GVHD góp ý | **Xong bản nộp.** Sửa số người thực nghiệm thành khoảng 3–5 người; xuất DOCX + PDF (7 trang) theo trình bày trang đề cương của báo cáo TLCN, vì portal không nhận `.md`. SV duyệt 16/09/2026 | commit `9e8dd3e` · file đính kèm trên portal |
| — | Chốt số người dùng thực nghiệm (D-017) | **Xong.** Khoảng 3–5 người — theo ngưỡng tham chiếu của rubric là Mức 3–4 của TC2.7; ngưỡng chính thức chốt ở bản cam kết. Đính chính D-013 (đã ghi nhầm "bắt buộc ≥ 10 người") | commit `9e8dd3e` — [`DECISIONS.md`](../DECISIONS.md) D-017 |
| P-03 | Làm rõ quan hệ giữa đề cương và bản cam kết sản phẩm | **Xong phần làm rõ.** Rubric không nhắc tới đề cương; bản cam kết là hồ sơ của Mục 2 Bước 3: phải có metric, có chữ ký SV + GVHD, bộ môn rà soát. Phần metric (§5 của bản cam kết) **chưa soạn** | commit `e056d7c` |
| P-12 | Dựng kiểm thử tự động; viết test cho các luồng cốt lõi | **Đang làm — xong đợt đầu.** Hạ tầng test theo D-018: settings riêng dùng SQLite trong bộ nhớ, không test nào chạm `.env`, Gemini hay VNPay thật (đã kiểm: chạy xanh trên bản sao không có `.env`). 48 test: đăng ký/đăng nhập 12, giỏ hàng 8, checkout 11, VNPay 5, trợ lý AI 12 — 43 xanh, 5 `xfail` tái hiện lỗi đã biết L-6 → L-10. Tự động hóa cả 5 test case thủ công TC_01 → TC_05 của TLCN | commit `d045ba7` (cấu hình), `f1417de`, `b8203bd`, `1467975` (test) |
| — | Ghi nhận 3 lỗi mới phát hiện khi viết test | **L-8** 🔴 mở thẳng trang "thanh toán thành công" là đơn online thành *đã thanh toán*, không qua VNPay · **L-9** AI vẫn đề nghị thêm sản phẩm đã hết hàng vào giỏ (trái UC-17) · **L-10** AI tìm thấy cả sản phẩm quản trị viên đã ẩn khỏi cửa hàng. Ghi vào [`COMMITMENT.md`](../COMMITMENT.md) §3, mỗi lỗi có một test `xfail` | test `xfail` trong commit `b8203bd` (L-8), `1467975` (L-9, L-10) |

## 2. Chỉ số trong tuần

| Chỉ số | Giá trị |
|---|---|
| Số commit | 9 tính tới 16/09/2026 — `9e8dd3e`, `560bdf0`, `e056d7c`, 4 commit test của P-12 (`d045ba7`, `f1417de`, `b8203bd`, `1467975`) và 2 commit tài liệu |
| Số Pull Request đã merge (có review) | 0 tính tới 16/09/2026 — PR `develop` → `main` sẽ mở trước lúc nộp |
| Số test tự động | 48 — 43 xanh, 5 `xfail` (lỗi đã biết, chưa sửa) |
| Số lần CI chạy / tỉ lệ build xanh | 0 — chưa có CI (P-10); test mới chạy trên máy cá nhân |
| Số lần deploy | 0 — chưa có hạ tầng KLTN (P-11) |
| Độ phủ test | 66% toàn bộ mã của 4 app (chạy tay 16/09/2026). Theo file: `core/views.py` 57%, `store_api/views.py` 73%, `userauths/views.py` 71%, `useradmin/views.py` 21% |
| Số defect còn tồn (Critical/Blocker) | 2 Critical — **L-6** (giá sản phẩm do trình duyệt gửi lên) và **L-8** (đơn online thành đã thanh toán khi chưa trả tiền); chưa sửa, đã có test tái hiện. Ngoài ra L-3, L-5, L-7, L-9, L-10 chưa phân mức |

## 3. Vướng mắc

- **Chưa rõ hình thức bản cam kết.** Rubric chỉ yêu cầu "thống nhất bằng văn bản"
  sản phẩm cuối cùng + bộ metric, có chữ ký SV và GVHD, trước mốc 50%; không quy
  định mẫu. Chưa biết GVHD muốn gộp phần này vào đề cương (dưới dạng phụ lục) hay
  làm văn bản riêng, và khoa có biểu mẫu riêng hay không.
- **Hai lỗi thanh toán Critical (L-6, L-8) chưa sửa.** Cả hai đã có test tái hiện.
  Theo quy trình, hướng xử lý các chỗ lệch (sửa code hay sửa đặc tả) chốt cùng GVHD
  trong bản cam kết; với L-6 và L-8 không có cách hiểu đặc tả nào chấp nhận được
  hành vi hiện tại, nên đề xuất sửa code ngay Tuần 3 thay vì chờ ký cam kết.
- **Kế hoạch Tuần 2 làm chưa hết.** Chưa trình bản cam kết, chưa chốt các chỗ lệch
  L-2 → L-7, chưa chọn hạ tầng KLTN (P-11) — chuyển sang Tuần 3.
- **Vẫn chưa có hạ tầng riêng cho KLTN** — như Tuần 1: `.env` còn trỏ tới
  production của TLCN nên chưa deploy được (D-002). Kiểm thử tự động không bị ảnh
  hưởng vì đã tách hẳn khỏi `.env`.

## 4. Kế hoạch tuần tới

**Tuần 3**: 21/09/2026 → 27/09/2026.

| ID | Việc dự kiến | Mục tiêu hoàn thành |
|---|---|---|
| P-08 | Sửa đề cương theo góp ý của GVHD (nếu có) | Góp ý ghi vào `tuan-03.md`, sửa thẳng `DE_CUONG.md` |
| P-03 | Hỏi GVHD hình thức bản cam kết; chốt L-2 → L-10; soạn nháp §5 metric kỹ thuật + ≥ 5 KPI nghiệp vụ | Có bản nháp §5; nếu GVHD đồng ý, sửa L-6 và L-8 kèm gỡ `xfail` |
| P-10 | Dựng CI tối thiểu trên GitHub Actions: cài đặt → kiểm tra → chạy 48 test hiện có, kèm độ phủ (P-13) | Có lần chạy CI đầu tiên trên `develop` |
| P-12 | Viết tiếp test cho `useradmin` (UC-19, UC-20, UC-26) và đánh giá sản phẩm (L-3) | Cả 4 app đều có test |
| P-11 | Chọn host, database, image storage cho KLTN | Ghi thành quyết định trong `DECISIONS.md` |
| P-05 | Giữ nhịp commit và báo cáo tuần | Nộp `tuan-03.md` trước 17:00 Thứ Sáu 25/09/2026 |

## 5. Ghi chú

**Quyết định mới** — [`../DECISIONS.md`](../DECISIONS.md):

| Mã | Nội dung |
|---|---|
| D-017 | Thực nghiệm với khoảng 3–5 người dùng thật; chấp nhận rủi ro không đạt Mức 5 của TC2.7 (cần ≥ 10 người). Kèm ghi chú đính chính dưới D-013 |
| D-018 | Kiểm thử tự động chạy trên settings riêng, SQLite trong bộ nhớ, không gọi dịch vụ ngoài; lỗi đã biết ghi bằng test `xfail` chặt kèm mã L-x |

**Chỉnh sửa đặc tả** — 1 lần, ghi tại [`../PLAN.md`](../PLAN.md) §6 dòng 5:
`SRS.md` §7 — đối chiếu TC_01 → TC_05 với test tự động; ghi nhận câu thông báo mong
đợi của TC_02 và TC_04 (TLCN ghi PASS) không có trong mã nguồn.

**Điều chỉnh kế hoạch** — thêm P-08 (nộp đề cương theo yêu cầu GVHD); ghi rõ ở
P-03 rằng đề cương không thay bản cam kết; bắt đầu P-12 sớm hơn kế hoạch (Giai đoạn 1
dự kiến từ Tuần 3); thêm L-8 → L-10 vào bản cam kết; chuyển P-11 và phần chốt các
chỗ lệch của P-03 sang Tuần 3.

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
được đính kèm để thầy góp ý nội dung. Em cũng bắt đầu sớm kiểm thử tự động: 48 test
cho các luồng cốt lõi, chưa sửa mã nguồn ứng dụng. Viết test phát hiện thêm 3 lỗi,
trong đó có một lỗi thanh toán nghiêm trọng.

**Đã làm**

- **P-08** — hoàn thiện đề cương KLTN: sửa số người dùng thực nghiệm thành khoảng
  3–5 người, xuất DOCX/PDF theo mẫu đề cương TLCN (commit `9e8dd3e`).
- **D-017** — chốt thực nghiệm với khoảng 3–5 người dùng; đính chính D-013 đã ghi
  nhầm "bắt buộc ≥ 10 người".
- **P-05** — ghi nhận hạn nộp báo cáo trước 17:00 Thứ Sáu và ý kiến của thầy cho
  Tuần 1.
- **P-03** — làm rõ khác biệt giữa đề cương và bản cam kết (commit `e056d7c`); phần
  metric chưa soạn.
- **P-12 (đang làm)** — dựng kiểm thử tự động bằng pytest (D-018), tách hẳn khỏi cấu
  hình production; 48 test cho đăng ký/đăng nhập, giỏ hàng, checkout, VNPay, trợ lý AI;
  tự động hóa 5 test case thủ công của TLCN.
- **Lỗi mới L-8, L-9, L-10** — mở thẳng trang "thanh toán thành công" là đơn online
  thành đã thanh toán; AI đề nghị thêm sản phẩm hết hàng vào giỏ; AI tìm thấy sản phẩm
  đã bị ẩn. Mỗi lỗi có một test tái hiện.

**Chỉ số**

- 9 commit, 0 Pull Request đã merge (tính tới 16/09/2026).
- 48 test tự động: 43 đạt, 5 lỗi đã biết đánh dấu `xfail`. Độ phủ 66% (chạy tay).
- CI: chưa có · Số lần deploy: 0.
- Defect Critical còn tồn: 2 — giá do trình duyệt gửi lên (L-6); đơn online thành đã
  thanh toán khi chưa trả tiền (L-8).

**Vướng mắc**

- Em xin ý kiến thầy về hình thức bản cam kết sản phẩm + metric: gộp vào đề cương
  dưới dạng phụ lục hay làm văn bản riêng để ký; khoa có biểu mẫu riêng không.
- Hai lỗi thanh toán Critical (L-6, L-8): em đề xuất sửa code ngay Tuần 3, không chờ
  ký bản cam kết.
- Kế hoạch Tuần 2 còn dở: chưa chốt các chỗ lệch giữa đặc tả và mã nguồn, chưa chọn
  hạ tầng riêng cho KLTN — chuyển sang Tuần 3.

**Kế hoạch tuần 3 (21/09 – 27/09/2026)**

- Sửa đề cương theo góp ý của thầy; soạn nháp phần metric và KPI của bản cam kết.
- Dựng CI trên GitHub Actions chạy bộ test hiện có; viết tiếp test cho trang quản lý
  của nhân viên.
- Sửa hai lỗi thanh toán L-6, L-8 nếu thầy đồng ý; chọn hạ tầng riêng cho KLTN.

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
- Commit; sau đó làm P-12: cài pytest + pytest-django, viết test cho luồng cốt lõi.
- Chia phần P-12 thành nhiều commit rồi push.
```

**Nội dung AI tạo ra**

```
Không sửa mã nguồn ứng dụng. AI tạo tài liệu và mã kiểm thử:
- Tài liệu: docs/weekly_report/README.md (lịch hạn nộp), tuan-01.md (ý kiến GVHD),
  _TEMPLATE.md, AGENTS.md/CLAUDE.md (§2, §6, §8, §9), DE_CUONG.md (số người thực
  nghiệm), PLAN.md, DECISIONS.md (D-017, D-018, đính chính D-013), COMMITMENT.md
  (L-8 → L-10), SRS.md §7, bản nháp báo cáo này.
- Mã kiểm thử (P-12): grocerly/grocerly/settings_test.py, pytest.ini, conftest.py,
  requirements-dev.txt, .coveragerc và 48 test trong core/tests, userauths/tests,
  store_api/tests; xóa 4 file tests.py rỗng.
- Script xuất đề cương sang DOCX/PDF (pandoc + bộ lọc Lua + LibreOffice); công cụ
  này đang ở thư mục tạm, chưa đưa vào repo.
AI đọc nguyên văn rubric (Mục 2, Mục 5, Mục 7, TC2.7) để trích dẫn, không tự đặt
ngưỡng. Mỗi test xfail được chạy lại để xác nhận nó hỏng đúng vì lỗi đã mô tả.
```

**Phần bạn đã sửa / hoàn thiện**

```
- Cung cấp hạn nộp và ý kiến GVHD; cung cấp báo cáo TLCN làm mẫu trình bày đề cương.
- Chốt khoảng 3–5 người dùng thực nghiệm và sửa lý do trong D-017: 3–5 người là con
  số làm được, 10 người là quá sức — ghi là rủi ro chấp nhận.
- Đọc và duyệt bản DOCX/PDF của đề cương trước khi nộp.
- Hỏi lại quan hệ giữa đề cương và bản cam kết, dẫn tới việc tách rõ hai văn bản
  trong PLAN.
- Yêu cầu chia phần P-12 thành nhiều commit theo nhóm rồi push lên develop.
- Lỗi của AI trong tuần (AI_USAGE_LOG mục 2, #14–#18): 3 lỗi trình bày trong công cụ
  xuất đề cương, D-013 ghi nhầm "bắt buộc ≥ 10 người", và một script sửa tài liệu
  bị dừng giữa chừng vì giả định dòng cuối file luôn có ký tự xuống dòng.
```

---

*Ý kiến GVHD:*
