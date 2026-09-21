# DECISIONS — Grocerly (KLTN)

Nhật ký các quyết định quan trọng của đồ án. Mỗi quyết định ghi lại **bối cảnh**,
**phương án đã cân nhắc**, **lựa chọn** và **lý do**.

Vì sao cần: rubric KLTN yêu cầu sinh viên giải thích được *vì sao* hệ thống được
làm như vậy, nêu được các phương án thay thế, và ghi nhận lý do cho mọi thay đổi
thiết kế (TC2.1 Mức 5, TC5). Trí nhớ không tái tạo được điều đó sau vài tháng —
file này thì có.

**Quy ước:**
- Mã `D-00x`, tăng dần, **không tái sử dụng** mã đã cấp.
- Trạng thái: `Đề xuất` → `Đã chốt` → (có thể) `Thay thế bởi D-0yy`.
- Quyết định đã chốt **không sửa nội dung**; muốn đổi thì thêm quyết định mới và
  đánh dấu cái cũ là bị thay thế. Lịch sử sai lầm cũng là bằng chứng.
- Quyết định ảnh hưởng tới đặc tả thì sửa thẳng [`SRS.md`](SRS.md) (yêu cầu) hoặc
  [`SDD.md`](SDD.md) (thiết kế), và ghi lần sửa đó vào [`PLAN.md`](PLAN.md) §6.

---

## D-001 · Áp dụng Spec Driven Development cho KLTN

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** KLTN kế thừa codebase TLCN đã hoàn chỉnh. Rubric KLTN
([link rubric](https://docs.google.com/document/d/17evZf7TPiTJqw-4n0xH_9l0PQuXZAKcc))
chấm theo minh chứng quá trình: thiếu minh chứng thì tiêu chí không được xếp từ
Mức 4 trở lên, và nội dung không giải thích được bị coi là đạo văn bất kể do AI
hay người viết.

**Phương án đã cân nhắc**

1. *Code trước, viết báo cáo sau* — cách làm ở TLCN. Nhanh lúc đầu, nhưng minh
   chứng quá trình phải dựng lại vào cuối kỳ, mà rubric yêu cầu nhiều thứ không
   back-fill được (tỉ lệ tuần có commit, lịch sử CI, số lần deploy).
2. *Spec Driven Development* — đặc tả dẫn đường, tài liệu sinh ra cùng lúc với code.
3. *Dùng công cụ quản lý dự án ngoài* (Jira/Notion) — minh chứng nằm ngoài repo,
   khó đối chiếu với lịch sử Git khi bảo vệ.

**Quyết định.** Chọn (2). Đặc tả, kế hoạch và quyết định nằm trong `docs/` cùng
repo, versioned bằng Git.

**Lý do.** Đặt minh chứng cạnh mã nguồn khiến chúng được cập nhật cùng nhịp với
code, và cho phép hội đồng đối chiếu trực tiếp tài liệu ↔ commit ↔ mã nguồn — đúng
cách rubric kiểm tra. Đây cũng là hàng rào chống việc "AI viết hộ mà không hiểu":
mọi thay đổi đều phải đi qua một dòng đặc tả do sinh viên viết ra.

---

## D-002 · Tách hoàn toàn hạ tầng KLTN khỏi hạ tầng TLCN

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** `grocerly/.env` hiện vẫn trỏ tới production của TLCN: host PaaS,
database Postgres đám mây và tài khoản Cloudinary đã dùng cho bài đã chấm điểm.

**Phương án đã cân nhắc**

1. *Dùng chung hạ tầng TLCN* — không tốn công thiết lập, nhưng mọi `migrate`,
   seed dữ liệu hay upload ảnh của KLTN sẽ ghi đè lên dữ liệu của bài đã nộp; ảnh
   và đơn hàng của hai đồ án trộn lẫn, không tách được minh chứng.
2. *Tách hoàn toàn* — host riêng, database riêng, image storage riêng.
3. *Dùng chung database nhưng khác schema* — vẫn chung một điểm hỏng, và một lệnh
   `migrate` sai schema là đủ để hỏng dữ liệu TLCN.

**Quyết định.** Chọn (2). KLTN dùng host, database và image storage riêng. Các key
phải trỏ lại: `DJANGO_SECRET_KEY` (sinh mới), `DJANGO_ALLOWED_HOSTS`,
`DATABASE_URL`, `CLOUDINARY_URL`; cùng `GEMINI_API_KEY` và nhóm `VNPAY_*` nếu dùng
tài khoản khác.

**Lý do.** TLCN đã được chấm điểm — dữ liệu của nó là bằng chứng của một bài nộp
đã hoàn tất và không được phép thay đổi. Tách hạ tầng cũng cho phép KLTN tự do
thử nghiệm (reset DB, đổi schema, seed dữ liệu test) mà không sợ hỏng gì.

**Hệ quả.** Trước mỗi lần `migrate` hoặc deploy phải xác nhận `.env` đang trỏ hạ
tầng KLTN. `grocerly/.env.example` hiện thiếu nhóm `VNPAY_*` mà `settings.py` có
đọc — cần bổ sung khi dựng env mới.

---

## D-003 · `AGENTS.md` là file hướng dẫn agent duy nhất, `CLAUDE.md` chỉ trỏ tới nó

- **Ngày:** 10/09/2026
- **Trạng thái:** ~~Đã chốt~~ → **Thay thế bởi D-006** (cùng ngày)

**Bối cảnh.** Đồ án dùng nhiều công cụ AI khác nhau. Mỗi công cụ có quy ước file
hướng dẫn riêng (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`).

**Phương án đã cân nhắc**

1. *Mỗi công cụ một file đầy đủ* — thực tế đã cho thấy hậu quả:
   `.github/copilot-instructions.md` viết từ giai đoạn đầu nay đã sai nhiều chỗ
   (nói dự án có 2 app trong khi thực tế có 4, nói "chưa có requirements.txt",
   ghi `decimal_places=3` trong khi mã nguồn dùng `2`, nói "không dùng DRF" trong
   khi `store_api` chạy trên DRF).
2. *Một file canonical + các file khác trỏ vào* — chỉ có một chỗ để cập nhật.

**Quyết định.** Chọn (2). `AGENTS.md` giữ toàn bộ nội dung; `CLAUDE.md` chỉ trỏ
tới nó cộng vài ghi chú riêng cho Claude Code.

**Lý do.** Tài liệu hướng dẫn sai còn nguy hiểm hơn không có tài liệu — nó khiến
agent tự tin làm sai. Một nguồn sự thật duy nhất khiến việc cập nhật rẻ đến mức
người ta thực sự chịu cập nhật.

**Hệ quả.** `.github/copilot-instructions.md` bị coi là lỗi thời. Cần cập nhật lại
hoặc xóa — theo dõi trong [`PLAN.md`](PLAN.md).

---

## D-004 · Giữ nguyên đặc tả TLCN làm baseline, thay đổi ghi thành delta

- **Ngày:** 10/09/2026
- **Trạng thái:** ~~Đã chốt~~ → **Thay thế bởi D-007** (cùng ngày)

**Bối cảnh.** Báo cáo TLCN đã đặc tả 26 use case, ERD 14 bảng, 27 màn hình và đã
được bảo vệ. KLTN cùng đề tài, cùng GVHD.

**Phương án đã cân nhắc**

1. *Viết lại đặc tả từ đầu cho KLTN* — tốn thời gian cho phần đã được chấp nhận,
   và tạo rủi ro đặc tả mới lệch khỏi mã nguồn đang chạy.
2. *Giữ baseline, ghi thay đổi thành delta* trong `SRS.md` §12.

**Quyết định.** Chọn (2).

**Lý do.** Hội đồng sẽ đối chiếu sơ đồ với mã nguồn tại buổi bảo vệ; đặc tả bám
sát code hiện có là điều kiện để đạt tỉ lệ khớp cao. Ghi delta còn cho thấy rõ
KLTN đã thêm được gì so với TLCN — chính là câu hỏi hội đồng sẽ hỏi.

---

## D-005 · Ưu tiên gỡ các "quy tắc chặn điểm" trước khi làm tính năng mới

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Rà soát repo ngày 10/09/2026 cho thấy đồ án đang vướng ba quy tắc
chặn điểm của rubric: **G5** (không có kiểm thử tự động — cả 4 `tests.py` đều là
stub 3 dòng), **G6** (không có CI/CD — `.github/` chỉ có file hướng dẫn Copilot,
không có `workflows/`), **G7** (chưa có thực nghiệm người dùng thật). Ngoài ra
lịch sử commit dồn cục theo đợt thay vì đều theo tuần.

**Phương án đã cân nhắc**

1. *Làm tính năng mới trước* (full-text search, live chat, ML recommendation) rồi
   bổ sung test và CI sau — trực quan hơn khi demo, nhưng ba gate kia chặn trần
   điểm bất kể tính năng tốt tới đâu.
2. *Gỡ gate trước, tính năng sau.*

**Quyết định.** Chọn (2): CI/CD + kỷ luật commit hằng tuần + AI Usage Log làm
trước, kế đến là bộ test tự động kèm coverage, rồi mới tới thực nghiệm người dùng
và các tính năng mới.

**Lý do.** Ba gate này chặn trần khoảng 9/20 điểm ở TC2.5 + TC2.6 + TC2.7 trước
khi hội đồng nhìn tới dòng code nào. Quan trọng hơn: chúng cần *thời gian tích
lũy* chứ không cần nhiều công. Pipeline dựng tuần cuối vẫn chỉ có vài lần chạy,
trong khi rubric đòi ≥10 lần deploy "trải đều theo tiến độ" — dựng sớm thì bằng
chứng tự sinh ra trong lúc mình làm việc khác.

---

## D-006 · `AGENTS.md` và `CLAUDE.md` là hai bản song sinh, mỗi bản tự đứng vững

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt — *thay thế D-003*

**Bối cảnh.** D-003 chọn cách để `AGENTS.md` giữ toàn bộ nội dung còn `CLAUDE.md`
chỉ trỏ vào. Cách đó tránh được việc trùng lặp, nhưng khiến `CLAUDE.md` không đọc
độc lập được: agent nào chỉ nạp `CLAUDE.md` sẽ chỉ thấy một cái con trỏ. Đồ án
cũng đã bỏ Copilot, nên chỉ còn hai file này cần đồng bộ với nhau.

**Phương án đã cân nhắc**

1. *Giữ nguyên D-003* — không trùng lặp, nhưng `CLAUDE.md` rỗng nghĩa nếu đọc một
   mình.
2. *Hai file nội dung đầy đủ, giống hệt nhau từ dòng 2* — mỗi file tự đứng vững;
   đổi lại phải sửa hai chỗ mỗi lần.
3. *Symlink `CLAUDE.md` → `AGENTS.md`* — Git trên Windows xử lý symlink không nhất
   quán, dễ biến thành file text chứa đường dẫn.

**Quyết định.** Chọn (2). Hai file giống hệt nhau từ dòng 2 trở đi, chỉ khác dòng
tiêu đề. Quy tắc đồng bộ ghi ngay đầu mỗi file kèm lệnh kiểm tra.

**Lý do.** Rủi ro thật của việc trùng lặp là *drift trong im lặng* — hai bản lệch
nhau mà không ai biết. Ở đây rủi ro đó kiểm tra được bằng một lệnh:

```bash
diff <(tail -n +2 AGENTS.md) <(tail -n +2 CLAUDE.md)
```

Trùng lặp mà phát hiện được bằng máy thì chấp nhận được; đánh đổi lấy việc mỗi
file đọc một mình vẫn đủ nghĩa là xứng đáng.

**Hệ quả.** Sửa một file thì phải sửa file kia trong cùng commit. Khi dựng CI
(P-10) nên thêm lệnh `diff` trên vào một chặng để máy tự canh thay cho con người.

---

## D-007 · `SRS.md` là tài liệu sống, sửa được; nhật ký sửa nằm trong `PLAN.md`

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt — *thay thế D-004*

**Bối cảnh.** D-004 coi đặc tả TLCN là bất biến và chỉ cho ghi thêm delta. Nhưng
đặc tả đó chưa hề được kiểm chứng lại với mã nguồn hiện tại, và nhiều khả năng có
chỗ sai hoặc đã lỗi thời — chính repo này đã có một ví dụ: file hướng dẫn Copilot
viết cùng thời kỳ ghi sai số lượng app, sai `decimal_places`, và nói dự án không
dùng DRF.

**Phương án đã cân nhắc**

1. *Đóng băng đặc tả, chỉ ghi delta* (D-004) — giữ được tính "nguyên bản", nhưng
   khóa luôn cả những chỗ sai, và người đọc phải ghép hai chỗ mới hiểu hệ thống
   thật sự làm gì.
2. *Cho sửa trực tiếp, ghi nhật ký sửa* — `SRS.md` luôn phản ánh hiện trạng; lịch
   sử thay đổi nằm ở nhật ký và ở Git.

**Quyết định.** Chọn (2). Sửa thẳng `SRS.md` cho đúng hiện trạng; mỗi lần sửa ghi
một dòng vào [`PLAN.md`](PLAN.md) §6 gồm sửa gì, vì sao, commit nào.

**Lý do.** Tại buổi bảo vệ, hội đồng đối chiếu ngẫu nhiên sơ đồ và đặc tả với mã
nguồn — thứ được chấm là *mức khớp*, không phải mức trung thành với báo cáo cũ.
Một đặc tả sai được giữ lại vì "báo cáo cũ viết vậy" là điểm trừ hai lần: sai ở
tài liệu, và cho thấy sinh viên chưa rà lại hệ thống của chính mình.

Đặt nhật ký sửa trong `PLAN.md` thay vì trong `SRS.md` để `SRS.md` chỉ trả lời một
câu hỏi duy nhất — *hệ thống làm gì* — còn mọi thứ mang tính tiến trình thì tập
trung một chỗ.

---

## D-008 · KLTN không mở rộng tính năng; ý tưởng mới đưa vào "hướng phát triển mở rộng"

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** TLCN đã liệt kê bốn hạn chế kèm hướng khắc phục: tìm kiếm full-text,
thống kê đa chiều, live chat thời gian thực, gợi ý bằng Machine Learning. Nhìn qua
thì đó là danh sách tính năng sẵn có để làm tiếp cho KLTN. Thời gian thực hiện là
15 tuần, từ 10/09/2026 đến 24/12/2026.

**Phương án đã cân nhắc**

1. *Làm 2–3 tính năng mới* — demo bắt mắt, nhưng mỗi tính năng lại kéo theo phần
   đặc tả, kiểm thử, tài liệu và thực nghiệm của riêng nó; trong khi bốn gate
   G3/G5/G6/G7 vẫn đang chặn ~11 điểm và không hề được gỡ.
2. *Không làm tính năng mới; dồn sức cho chất lượng phần cốt lõi* — kiểm thử, CI/CD,
   đặc tả, thực nghiệm người dùng.

**Quyết định.** Chọn (2). Các ý tưởng mở rộng được viết ở mục *"Các hướng phát
triển mở rộng"* cuối báo cáo (P-31), không cài đặt trong KLTN.

**Lý do.** Rubric không cho điểm cho số lượng tính năng. Điểm nằm ở mức hoàn thiện
so với **những gì đã cam kết** (TC2.2), ở kiểm thử, CI/CD và thực nghiệm người
dùng. Một hệ thống 26 use case chạy chắc, có test, có CI, có UAT sẽ ăn đứt hệ
thống 30 use case mà không có gì trong số đó.

Còn một rủi ro nữa: rubric ghi rõ nội dung không giải thích được là đạo văn, và
hai chỗ như vậy là 0 điểm toàn bài. Tính năng làm vội (nhất là phần ML) chính là
loại code dễ rơi vào tình trạng "chạy được nhưng không giải thích nổi".

**Hệ quả.** Có tính năng mới nào muốn thêm thì phải qua một quyết định mới ở file
này, và phải nêu rõ đánh đổi với thời gian còn lại.

---

## D-009 · Đặt tên tài liệu đặc tả là `SRS.md` thay vì `PRD.md`

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Tài liệu đặc tả ban đầu được đặt tên `PRD.md` (Product Requirements
Document). Rubric KLTN, Mục 8 — Danh mục hồ sơ minh chứng bắt buộc — ghi nguyên
văn: *"Tài liệu đặc tả yêu cầu và thiết kế (SRS/SDD) kèm theo các sơ đồ thiết kế"*,
phục vụ TC2.1.

**Phương án đã cân nhắc**

1. *Giữ tên `PRD.md`* — quen thuộc trong ngành phần mềm thương mại, nhưng không
   khớp thuật ngữ mà rubric và hội đồng dùng.
2. *Đổi thành `SRS.md`* — đúng tên trong danh mục hồ sơ, và đúng bản chất nội dung.

**Quyết định.** Chọn (2). Đổi `docs/PRD.md` → `docs/SRS.md`, cập nhật toàn bộ 26
dòng tham chiếu trong `AGENTS.md`, `CLAUDE.md`, `PLAN.md`, `DECISIONS.md` và
`weekly_report/`.

**Lý do.** PRD và SRS trả lời hai câu hỏi khác nhau: PRD nghiêng về *vì sao làm*
(thị trường, chân dung người dùng, mục tiêu kinh doanh), SRS nghiêng về *hệ thống
phải làm gì* theo cách kiểm chứng được (FR, NFR, use case, acceptance criteria).
Nội dung file này vốn đã là loại thứ hai, nên tên cũ vừa sai bản chất vừa lệch
thuật ngữ của hội đồng. Khi hội đồng rà hồ sơ minh chứng, họ tìm "SRS".

**Hệ quả.** Ranh giới SRS/SDD được ghi chú ngay đầu `SRS.md`: file hiện gộp cả yêu
cầu (Mục 1–6) lẫn thiết kế (Mục 7–9). Việc tách được chốt riêng ở D-010.

---

## D-010 · Tách tài liệu đặc tả thành `SRS.md` (yêu cầu) và `SDD.md` (thiết kế)

- **Ngày:** 10/09/2026
- **Trạng thái:** ~~Đã chốt — thực hiện ở P-27, sau P-24~~ → **Thay thế bởi D-011** (cùng ngày)

**Bối cảnh.** `SRS.md` hiện gộp hai loại nội dung khác bản chất: Mục 1–6 là *yêu
cầu* (hệ thống phải làm gì), Mục 7–9 là *thiết kế* (mô hình dữ liệu, giao diện,
công nghệ — hệ thống được xây thế nào). Rubric Mục 8 liệt kê hồ sơ là "SRS/SDD",
tức là chấp nhận cả hai dạng, nhưng TC2.1 Mức 5 lại đòi **≥ 4 loại sơ đồ thiết kế**
khớp 100% với mã nguồn — phần thiết kế sẽ phình ra đáng kể khi làm P-24.

**Phương án đã cân nhắc**

1. *Giữ một file gộp* — ít file hơn, nhưng khi thêm đủ 4 loại sơ đồ thì tài liệu
   thành một khối lẫn lộn, và người đọc muốn tra một yêu cầu phải lội qua sơ đồ.
2. *Tách ngay bây giờ* — sạch về mặt cấu trúc, nhưng Mục 7–9 hiện mới là bảng tóm
   tắt kế thừa từ TLCN, chưa rà lại; tách lúc này chỉ là chuyển chỗ mấy cái bảng.
3. *Tách sau khi rà xong phần thiết kế* (P-24) — tách một lần, đúng lúc nội dung
   đã đủ hình hài.

**Quyết định.** Chọn (3). `SRS.md` giữ Mục 1–6 (yêu cầu); `SDD.md` nhận Mục 7–9
cùng các sơ đồ thiết kế được cập nhật ở P-24. Thực hiện tại P-27.

**Lý do.** Hai tài liệu trả lời hai câu hỏi cho hai người đọc khác nhau: SRS trả
lời *"hệ thống phải làm gì"* — dùng để viết acceptance criteria và test; SDD trả
lời *"xây thế nào"* — dùng khi hội đồng đối chiếu sơ đồ với mã nguồn. Gộp lại thì
mỗi lần sửa một bên đều đụng vào file của bên kia, và lịch sử Git khó đọc.

Chọn tách *sau* P-24 thay vì ngay bây giờ vì tách một tài liệu chưa rà lại chỉ tạo
ra hai tài liệu chưa rà lại — công việc thật nằm ở khâu kiểm chứng nội dung với mã
nguồn, không nằm ở khâu chia file.

**Hệ quả.** Khi tách, cập nhật tham chiếu ở `AGENTS.md`/`CLAUDE.md`, `PLAN.md`,
`AI_USAGE_LOG.md`, `weekly_report/`, và ghi một dòng vào `PLAN.md` §6.

---

## D-011 · Tách `SRS.md` và `SDD.md` ngay từ đầu, trước khi rà soát nội dung

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt — *thay thế D-010*

**Bối cảnh.** D-010 chọn hoãn việc tách tới sau P-24 với lý do "tách một tài liệu
chưa rà lại chỉ tạo ra hai tài liệu chưa rà lại". Nhưng Giai đoạn 2 có hai việc
lớn chạy song song trên đúng hai nửa của file: rà soát đặc tả + viết acceptance
criteria (P-23, nửa yêu cầu) và cập nhật sơ đồ thiết kế (P-24, nửa thiết kế).

**Phương án đã cân nhắc**

1. *Tách sau P-24* (D-010) — tách một lần khi nội dung đã đủ hình hài, nhưng mọi
   lần sửa ở P-23 và P-24 đều dồn vào một file; tới lúc tách, lịch sử Git của
   phần thiết kế bị cắt ở ngày tách, và dấu vết quá trình rà soát (chính là minh
   chứng) nằm lẫn trong lịch sử của `SRS.md`.
2. *Tách ngay từ đầu* (Giai đoạn 0) — việc tách chỉ là chuyển Mục 7–9 sang file
   mới, rất ít công; từ đó mỗi việc chỉ đụng tới một file.

**Quyết định.** Chọn (2). Tách tại P-07, trước P-23 và P-24. `SRS.md` giữ Mục 1–6
(yêu cầu); `SDD.md` nhận Mục 7–9 (thiết kế).

**Lý do.** Rubric chấm quá trình qua lịch sử Git. Khi hai tài liệu tách riêng từ
đầu, `git log docs/SDD.md` cho thấy trọn vẹn quá trình thiết kế được rà lại và
bổ sung sơ đồ, `git log docs/SRS.md` cho thấy quá trình sửa yêu cầu và viết AC —
mỗi bên đọc được độc lập. Chi phí tách lúc này thấp nhất vì chưa có nội dung mới
nào phải di chuyển theo.

**Hệ quả.** P-27 bị bỏ, thay bằng P-07 ở Giai đoạn 0. Khi tách, cập nhật tham
chiếu ở `AGENTS.md`/`CLAUDE.md` (§1 bảng tài liệu điều hướng), `PLAN.md`,
`AI_USAGE_LOG.md`, `weekly_report/`, bỏ ghi chú "sẽ tách" ở đầu `SRS.md`, và ghi
một dòng vào `PLAN.md` §6.

---

## D-012 · Làm một mình vẫn làm việc theo nhánh và tự tạo Pull Request

- **Ngày:** 10/09/2026
- **Trạng thái:** ~~Đã chốt~~ → **Thay thế bởi D-016** (11/09/2026)

**Bối cảnh.** KLTN do một sinh viên thực hiện. Rubric TC2.4 Mức 5 yêu cầu
*"≥ 90% thay đổi đi qua Pull Request có review"* (Mức 4: ≥ 60%, Mức 3: ≥ 30%), và
mô tả Mức 3 là *"chủ yếu làm việc trên một nhánh, ít review"*. Rubric không miễn
tiêu chí này cho đồ án một người: Bước 1 ghi "số lượng sinh viên dự kiến", Bước 2
chỉ đặt yêu cầu phân công cho *"nhóm nhiều sinh viên"* — tức là có tính tới trường
hợp làm một mình. Mặt khác, GitHub không cho tác giả PR tự bấm *Approve*.

**Phương án đã cân nhắc**

1. *Commit thẳng lên `main`* — nhanh nhất, nhưng TC2.4 khó vượt Mức 3, và CI
   không có chỗ để chạy kiểm tra *trước khi* thay đổi vào `main`.
2. *Nhánh + PR, mời GVHD review* — đúng nghĩa "có review" nhất, nhưng không thực
   tế nếu mỗi tuần có nhiều PR.
3. *Nhánh + tự tạo PR, định nghĩa rõ "review" cho đồ án một người* — mỗi PR phải
   qua CI xanh, checklist tự review, và một lượt review bằng AI đăng thành comment.

**Quyết định.** Chọn (3). Mỗi việc P-xx làm trên một nhánh riêng, merge vào `main`
qua PR. Cách hiểu "review" ở trên được ghi vào bản cam kết P-03 để GVHD ký xác
nhận — rubric Mục 5 cho phép điều chỉnh ngưỡng metric tại Bước 3.

**Lý do.** Chi phí mỗi PR chỉ vài phút, trong khi một PR đồng thời sinh minh chứng
cho ba tiêu chí: TC2.4 (tỉ lệ thay đổi qua PR), TC2.6 (lịch sử CI chạy trên từng
PR) và TC2.3 (checklist kiểm soát đầu ra AI được áp dụng có hệ thống, xem
`AI_USAGE_LOG.md` §3). Ghi cách hiểu "review" vào bản cam kết để hội đồng không
bắt bẻ được việc tự review.

**Hệ quả.** Bật branch protection cho `main` (bắt buộc qua PR, bắt buộc CI xanh)
khi đã có CI ở P-10. Nếu repo để private thì cần GitHub Pro — có miễn phí trong
GitHub Student Developer Pack.

---

## D-013 · Gộp khảo sát bên liên quan (TC1) vào buổi thực nghiệm người dùng (TC2.7)

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** TC1 cần tiếp xúc bên liên quan thực tế: 0 người thì rơi xuống Mức 2
("nhu cầu chỉ dựa trên suy đoán"), ≥ 1 → Mức 3, ≥ 2 → Mức 4, ≥ 3 hoặc ≥ 30 phiếu →
Mức 5. Đồ án một người, quy mô nhỏ, khó tìm riêng 2–3 người để khảo sát. Trong
khi đó TC2.7 (P-25) vẫn bắt buộc phải có ≥ 10 người dùng thật thuộc nhóm mục tiêu.

> *Đính chính 15/09/2026:* câu trên chưa chính xác — ≥ 10 người là ngưỡng Mức 5 của
> TC2.7, không phải điều kiện bắt buộc (≥ 3 người đã là Mức 3). Số người thực
> nghiệm được chốt lại ở D-017.

**Phương án đã cân nhắc**

1. *Hai đợt riêng: khảo sát sớm (P-22) và thực nghiệm sau (P-25)* — dữ liệu nhu
   cầu có sớm để làm căn cứ chốt KPI, nhưng phải tìm người hai lần.
2. *Bỏ khảo sát* — TC1 chặn ở Mức 2 (tối đa 5,5/10).
3. *Gộp vào P-25* — mỗi buổi thực nghiệm dành ~5 phút đầu phỏng vấn thói quen mua
   thực phẩm, rồi mới làm tác vụ và đo SUS. Tìm người một lần, dùng cho cả hai
   tiêu chí.

**Quyết định.** Chọn (3). P-22 gộp vào P-25. Biên bản mỗi buổi ghi tách hai phần:
phỏng vấn nhu cầu (minh chứng TC1) và kết quả tác vụ + SUS (minh chứng TC2.7).

**Lý do.** Khó khăn thật là tìm được người, và việc đó dù sao cũng phải làm cho
P-25. Gộp lại thì TC1 có dữ liệu mà không tốn thêm lượt tìm người nào; nếu P-25 đạt
≥ 3 người thì TC1 cũng đủ ngưỡng Mức 5 về số bên liên quan.

**Hệ quả.** Dữ liệu nhu cầu tới muộn (Tuần 12), sau mốc chốt KPI ở P-03 (Tuần 7).
KPI nghiệp vụ vì vậy phải chốt dựa trên bài toán đã nêu trong TLCN, và phần phỏng
vấn ở P-25 đóng vai trò *kiểm chứng lại* KPI đó. Khi bảo vệ, nếu hội đồng hỏi
"vì sao khảo sát sau khi chốt KPI" thì câu trả lời nằm ở đây.

---

## D-014 · Không đưa công cụ agent (`.claude/`) vào repository

- **Ngày:** 10/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Bộ công cụ ECC (everything-claude-code) cho Claude Code được cài vào
`.claude/` của repo: 818 file, khoảng 165.000 dòng (agent, skill, rule, hook,
khoảng 200 script). Nó từng được commit ở một nhánh local nhưng chưa push. Đây là
môi trường làm việc cá nhân của sinh viên, không phải một phần của sản phẩm.

**Phương án đã cân nhắc**

1. *Commit `.claude/` vào repo* — ai clone về cũng có cùng bộ công cụ. Nhưng
   repo là hồ sơ minh chứng số 4 (rubric Mục 8): linter và phân tích tĩnh (TC2.4)
   sẽ quét cả khối script bên thứ ba này, làm sai lệch tỉ lệ lỗi lint và tỉ lệ
   trùng lặp; và hội đồng có thể chọn ngẫu nhiên một file trong đó để hỏi — nội
   dung không giải thích được bị tính là đạo văn (Mục 6).
2. *Ignore `.claude/` trong repo* — công cụ vẫn nằm trên máy và vẫn chạy, repo
   chỉ chứa sản phẩm và tài liệu của đồ án.
3. *Cài ECC ở cấp người dùng (`~/.claude`)* — sạch nhất, nhưng phải cài lại bộ
   công cụ và sửa đường dẫn hook; không cần thiết khi (2) đã đạt mục tiêu.

**Quyết định.** Chọn (2). Thêm `.claude/` vào `.gitignore`; bỏ commit cài ECC chưa
push, giữ nguyên file trên đĩa.

**Lý do.** Mọi thứ nằm trong repo đều là thứ sinh viên phải bảo vệ được. Công cụ
hỗ trợ làm việc thì cần *kê khai*, không cần *nộp*: việc dùng Claude Code và ECC
được ghi trong `AI_USAGE_LOG.md`, còn các quy ước thật sự ràng buộc dự án đã nằm
trong `AGENTS.md`/`CLAUDE.md` — hai file này vẫn được commit.

**Hệ quả.** Các rule trong `.claude/rules/` không được version bằng Git; quy ước
nào cần ràng buộc dự án thì phải đưa vào `AGENTS.md`/`CLAUDE.md`. Máy khác clone
repo về sẽ không có bộ công cụ này — chấp nhận được vì đồ án chỉ có một người làm.

---

## D-015 · Grocerly là mô hình một nhà bán, không phải marketplace nhiều người bán

- **Ngày:** 11/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Đặc tả TLCN mô tả tác nhân A3 là "Người bán" vận hành *gian hàng
riêng* với thống kê riêng, và `README.md` quảng cáo "Multi-Vendor System". Mã
nguồn không làm như vậy: không có vai trò người bán riêng; mọi tài khoản
`is_staff` vào `/useradmin/` đều thấy toàn bộ sản phẩm, đơn hàng và doanh thu.
Model `Vendor` chỉ là hồ sơ nhà cung cấp (tên, ảnh, địa chỉ, liên hệ) gắn vào sản
phẩm. Khi soạn bản cam kết P-03 phải chốt theo một phía (chỗ lệch L-1).

**Phương án đã cân nhắc**

1. *Làm marketplace đúng như đặc tả TLCN* — thêm vai trò người bán, lọc sản phẩm/
   đơn hàng/doanh thu theo người bán, đăng ký gian hàng. Đây là tính năng mới đụng
   tới phân quyền và mọi truy vấn ở `useradmin` — ngoài phạm vi KLTN (D-008).
2. *Giữ mô hình một nhà bán, sửa đặc tả cho khớp mã nguồn* — một cửa hàng bán hàng
   của nhiều nhà cung cấp; A3 là nhân viên của cửa hàng đó.

**Quyết định.** Chọn (2).

**Lý do.** Đây là mô hình mã nguồn đang chạy thật, và đúng với bài toán đề tài
đặt ra (một cửa hàng thực phẩm cần công cụ bán online + trợ lý AI). Sửa đặc tả
khiến hội đồng đối chiếu thấy khớp; làm marketplace thì tốn công cho một tính năng
không ai yêu cầu, trong khi các gate G5/G6/G7 vẫn đang chặn điểm.

**Hệ quả.**
- `SRS.md`: A3 đổi thành *Nhân viên cửa hàng*; các chỗ "người bán / gian hàng" đổi
  thành "nhân viên / cửa hàng". Mã yêu cầu `FR-V-xx` giữ nguyên để không gãy truy vết.
- `README.md` bỏ mô tả "Multi-Vendor".
- "Nhà cung cấp" (`Vendor`) giữ nguyên nghĩa là nguồn hàng, không phải tài khoản.
  Trường `Vendor.user` là phần sót lại từ template gốc, chưa có vai trò nghiệp vụ.
- Marketplace đưa vào mục "Các hướng phát triển mở rộng".

---

## D-016 · Làm việc trên nhánh `develop`, merge vào `main` qua Pull Request

- **Ngày:** 11/09/2026
- **Trạng thái:** Đã chốt — *thay thế D-012*

**Bối cảnh.** D-012 chọn mỗi việc P-xx một nhánh riêng tách từ `main`. Sau hai PR
đầu tiên, cách này lộ hai vấn đề. Một: mỗi việc nhỏ đều phải tạo nhánh, PR, merge,
xóa nhánh — tốn công so với một đồ án một người. Hai: thực tế công việc không chia
gọn theo P-xx; nhánh `docs/product-commitment` (PR #2) cuối cùng chứa ba việc khác
nhau là D-015, bản cam kết P-03 và đề cương KLTN, nên tên nhánh không còn đúng với
nội dung.

**Phương án đã cân nhắc**

1. *Giữ D-012* — mỗi PR gọn một việc, dễ truy vết; nhưng tốn công, và như PR #2
   cho thấy, nhánh vẫn trôi khỏi phạm vi ban đầu.
2. *Commit thẳng lên `main`* — nhanh nhất, nhưng mất tỉ lệ thay đổi qua PR mà
   TC2.4 chấm (Mức 3 trở xuống), và CI không có chỗ chạy trước khi vào `main`.
3. *Một nhánh `develop` sống lâu dài* — mọi việc commit trên `develop`, định kỳ mở
   PR `develop` → `main`.
4. *Git Flow đầy đủ* — nhánh tính năng tách từ `develop` rồi mới lên `main`; còn
   nhiều bước hơn cả D-012.

**Quyết định.** Chọn (3). Mọi thay đổi commit trên `develop`; `main` chỉ nhận thay
đổi qua PR từ `develop`, merge bằng *merge commit* (không squash/rebase).

**Lý do.** Mọi commit vào `main` vẫn đi qua PR, nên tỉ lệ thay đổi qua PR mà TC2.4
đo vẫn là 100%; CI vẫn có chỗ chạy trước khi vào `main`. Đổi lại chỉ còn một nhánh
phải quản lý. Merge commit giữ nguyên hash của từng commit — cần thiết vì
`AI_USAGE_LOG.md` đối chiếu từng phiên với hash commit.

Đánh đổi là mỗi PR sẽ to hơn và gồm nhiều việc, khó review hơn. Khắc phục bằng
cách merge đều đặn (xem Hệ quả) để PR không phình ra.

**Hệ quả.**
- Nhánh `develop` tạo từ `main` ngày 11/09/2026.
- Mở PR `develop` → `main` **ít nhất mỗi tuần một lần**; mô tả PR liệt kê các việc
  P-xx và quyết định có trong đó.
- Cách hiểu "review" cho đồ án một người giữ nguyên như D-012: CI xanh, checklist
  tự review, một lượt review bằng AI đăng thành comment — áp dụng cho từng PR
  `develop` → `main`. Ghi vào bản cam kết P-03.
- Khi có CI (P-10): bật branch protection cho `main` (bắt buộc qua PR, bắt buộc CI
  xanh); `develop` không cần khóa.

---

## D-017 · Thực nghiệm người dùng với khoảng 3–5 người

- **Ngày:** 15/09/2026
- **Trạng thái:** Đã chốt — rủi ro chấp nhận (*accepted risk*)

**Bối cảnh.** Đề cương, P-25 và D-013 đặt mục tiêu ≥ 10 người dùng thật cho thực
nghiệm. Khi soạn đề cương nộp GVHD, SV chốt lại con số khoảng 3–5 người. Đọc lại
rubric thì ≥ 10 người không phải điều kiện bắt buộc như D-013 viết, mà là ngưỡng
Mức 5 của TC2.7. Theo ngưỡng tham chiếu ở Mục 5 của rubric: ≥ 3 người là Mức 3,
≥ 5 người là Mức 4, ≥ 10 người là Mức 5; và SV cùng GVHD được phép điều chỉnh
ngưỡng khi chốt bản cam kết (Bước 3).

**Phương án đã cân nhắc**

1. *Giữ ≥ 10 người* — mở đường tới Mức 5 của TC2.7, nhưng phải tìm đủ hơn 10 người
   đúng nhóm đối tượng và tổ chức từng buổi trong Tuần 10–12, một mình.
2. *Khoảng 3–5 người* — làm được chắc chắn hơn; theo ngưỡng tham chiếu, TC2.7 dừng
   ở Mức 3 (3–4 người) hoặc Mức 4 (5 người).
3. *Ghi 3–5 người ở đề cương nhưng giữ ≥ 10 người ở kế hoạch* — tài liệu tự mâu
   thuẫn, hội đồng đối chiếu là thấy.

**Quyết định.** Chọn (2). Đề cương và P-25 ghi khoảng 3–5 người dùng thật thuộc
nhóm đối tượng mục tiêu.

**Lý do.** 3–5 người là con số SV dự tính làm được; 10 người là hơi quá. SV chấp
nhận rủi ro về điểm (*accepted risk*): theo ngưỡng tham chiếu, TC2.7 mất tối đa
khoảng 0,75 điểm (5 người, Mức 4) đến 1,5 điểm (3–4 người, Mức 3) so với Mức 5. TC1 không bị ảnh hưởng: 3 người phỏng vấn đã đủ ngưỡng
Mức 5 về số bên liên quan (D-013).

**Hệ quả.**
- Sửa `DE_CUONG.md` (§1, §2.2, bảng kế hoạch §5) và P-25 trong `PLAN.md`.
- D-013 giữ nguyên văn, thêm ghi chú đính chính trỏ về đây.
- Khi soạn bản cam kết P-03, ghi rõ ngưỡng số người dùng thực nghiệm đã thống nhất
  với GVHD.

---

## D-018 · Kiểm thử tự động chạy trên settings riêng, SQLite trong bộ nhớ, không gọi dịch vụ ngoài

- **Ngày:** 16/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** P-12 dựng bộ test tự động đầu tiên. `AGENTS.md`/`CLAUDE.md` §8 đã
chọn pytest + pytest-django; còn phải chốt test chạy trên database nào, tách dịch
vụ ngoài ra sao, và xử lý các lỗi đã biết (L-x) thế nào. Ràng buộc: `settings.py`
chép **mọi** key của `.env` vào `os.environ`, ghi đè cả biến môi trường đã đặt sẵn,
mà `.env` hiện vẫn trỏ tới database, Cloudinary và khóa Gemini production của TLCN
(D-002).

**Phương án đã cân nhắc**

1. *Database cho test*
   - (a) Dùng `settings.py`, đổi database bằng biến môi trường — không làm được vì
     `.env` ghi đè; sơ suất một lần là pytest-django tạo database `test_…` ngay trên
     server production.
   - (b) File `grocerly/settings_test.py` import `settings.py` rồi ghi đè
     `DATABASES` sang SQLite trong bộ nhớ — nhanh, không cần cài thêm gì, chạy được
     cả khi không có `.env` (CI). Đánh đổi: SQLite khác PostgreSQL của production ở
     vài chỗ (so khớp không phân biệt hoa thường với chữ có dấu, kiểu Decimal), có
     thể che lỗi chỉ xảy ra trên PostgreSQL.
   - (c) PostgreSQL riêng cho test (Docker) — giống production nhất, nhưng lần chạy
     test nào trên máy cá nhân cũng phải bật Docker.
2. *Lỗi đã biết nhưng chưa sửa*
   - (a) Chưa viết test cho tới khi sửa — lỗi không được chứng minh bằng test.
   - (b) Viết test và để đỏ — bộ test đỏ thường trực, không phân biệt được lỗi cũ
     với lỗi mới phát sinh.
   - (c) Viết test mô tả hành vi **đúng**, đánh dấu `xfail` kèm mã L-x, bật
     `xfail_strict` — bộ test vẫn xanh, lỗi được tái hiện; khi sửa xong, test
     chuyển XPASS làm bộ test đỏ, buộc gỡ dấu `xfail`, test đó thành regression test.
3. *Dữ liệu test* — fixture pytest viết tay, hoặc thư viện factory_boy /
   model_bakery. Fixture viết tay không thêm thư viện, đọc là hiểu.

**Quyết định.** Chọn 1(b), 2(c), fixture viết tay. Kèm theo:
- **Gemini:** `settings_test.py` xóa trắng `GEMINI_API_KEY`; test cần câu trả lời
  thì thay model bằng `MagicMock` — không test nào gọi được Gemini thật.
- **VNPay:** merchant và secret giả; test tự ký phản hồi VNPay bằng HMAC-SHA512,
  viết độc lập với `core/vnpay.py` để không dùng lại chính đoạn code đang kiểm.
- **File upload:** `InMemoryStorage`, không lên Cloudinary, không ghi `media/`.
- **Chốt chặn:** `grocerly/conftest.py` dừng pytest nếu database không phải SQLite
  — chặn trường hợp chạy nhầm `pytest --ds=grocerly.settings`.
- **Thư viện test** nằm trong `grocerly/requirements-dev.txt` (kế thừa
  `requirements.txt`), không vào image production.

**Lý do.** Ưu tiên số một là không chạm vào hạ tầng TLCN (D-002) và chạy được trên
CI không có `.env` (P-10). Hai điều này đã kiểm chứng ngày 16/09/2026: chốt chặn
dừng đúng khi trỏ settings sang PostgreSQL; bộ test chạy xanh trên bản sao mã nguồn
không có `.env`. Rủi ro lệch SQLite/PostgreSQL được chấp nhận ở giai đoạn này; xem
lại khi dựng CI — có thể thêm một job chạy trên PostgreSQL.

**Hệ quả.**
- Chạy test: `cd grocerly && pytest`; kèm độ phủ: `pytest --cov`.
- Viết test phát hiện thêm ba chỗ lệch L-8, L-9, L-10 — ghi vào `COMMITMENT.md` §3.
- Khi sửa một lỗi L-x: gỡ `xfail` của test tương ứng **trong cùng commit sửa**.
- Cập nhật `AGENTS.md`/`CLAUDE.md` §6, §8, §9.

---

## D-019 · CI chạy trên GitHub Actions, dựng dần từng chặng theo backlog

- **Ngày:** 17/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Gate G6 chặn TC2.6 ở 2,75/5 khi repo không có CI. Mức 5 cần pipeline
≥ 6 chặng (build → lint → test → quét secret → đóng gói → deploy) và lịch sử chạy
tích lũy theo thời gian (AGENTS.md §4c). Hiện chỉ có đủ điều kiện cho một phần: bộ
test đã chạy được không cần `.env` (D-018), nhưng chưa có linter (P-14), chưa cấu
hình gitleaks (P-15), chưa có hạ tầng KLTN để deploy (P-11, D-002).

**Phương án đã cân nhắc**

1. *Nền tảng CI*
   - (a) **GitHub Actions** — repo đã ở GitHub, không cần tài khoản thêm; miễn phí
     cho repo public, repo private có hạn mức phút chạy; kết quả gắn thẳng vào
     commit và PR, là minh chứng hội đồng xem được ngay.
   - (b) GitLab CI, CircleCI, Jenkins — phải mirror repo hoặc tự vận hành server;
     không đem lại gì thêm cho đồ án một người.
2. *Thời điểm dựng*
   - (a) Chờ đủ lint, quét secret, hạ tầng rồi dựng một lần đủ 6 chặng — mất vài
     tuần lịch sử chạy CI không back-fill được.
   - (b) Dựng ngay với các chặng đã làm được, mỗi việc P-14, P-15, P-11 xong thì
     thêm chặng tương ứng vào cùng file workflow.

**Quyết định.** Chọn 1(a), 2(b). File `.github/workflows/ci.yml`, chạy khi push lên
`develop`, `main` và khi mở PR vào `main`. Bản đầu gồm hai job:
- `twin-files` — so `AGENTS.md` với `CLAUDE.md` từ dòng 2 (thực hiện hệ quả của D-006).
- `test` — trên Python 3.12 (cùng bản với `Dockerfile`), với `grocerly.settings_test`:
  cài `requirements-dev.txt` (build) → `manage.py check` → `makemigrations --check
  --dry-run` (model đổi mà thiếu migration thì đỏ) → `pytest --cov` → ghi bảng độ phủ
  vào trang tóm tắt của lần chạy và lưu `coverage.xml` làm artifact (P-13).

Workflow chỉ có quyền đọc repo (`permissions: contents: read`) và không dùng secret
nào của repository.

**Lý do.** Lịch sử CI là minh chứng tích lũy; dựng sớm với 2 job chạy thật có giá
trị hơn một pipeline đủ chặng dựng muộn. Chưa thêm job PostgreSQL mà D-018 để ngỏ:
chưa có lỗi nào chỉ xảy ra trên PostgreSQL, thêm vào lúc này là thêm thứ phải giải
thích mà chưa cần — xem lại khi có hạ tầng KLTN (P-11).

**Hệ quả.**
- Chạy thử toàn bộ các bước trên bản sao sạch (không `.env`, Python 3.12) ngày
  17/09/2026: xanh, 43 passed + 5 xfailed, độ phủ 66%.
- Chặng kiểm tra migration phát hiện ngay model `CartOrder` lệch migration — xem D-020.
- Thêm chặng khi xong P-14 (lint), P-15 (gitleaks), P-11 (đóng gói image + deploy).
- Bật branch protection cho `main`, bắt buộc CI xanh (D-016) — SV thao tác trong
  phần cài đặt repo trên GitHub.
- Cập nhật `AGENTS.md`/`CLAUDE.md` §6, §8.

---

## D-020 · Thêm migration xóa cột `stripe_payment_intent` cho khớp model

- **Ngày:** 17/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Chặng `makemigrations --check` của CI (D-019) báo model và migration
lệch nhau. Commit TLCN `51c4b96` (*Add VNPay payment integration*, 15/06/2026) bỏ
Stripe, xóa trường `stripe_payment_intent` khỏi model `CartOrder` nhưng không sinh
migration. Mọi database đã `migrate` vẫn còn cột này (kiểu chuỗi, cho phép `NULL`);
code không còn đọc hay ghi nó nên chưa gây lỗi.

**Phương án đã cân nhắc**
1. *Sinh migration `0005` xóa cột* — model và schema khớp lại; migration chỉ có tác
   dụng khi chạy `migrate`, nên không đụng database TLCN đang chạy. Đánh đổi: dữ liệu
   cũ trong cột (nếu có) mất khi migrate — không đáng kể vì Stripe đã bỏ.
2. *Thêm lại trường vào model* — giữ cột thừa của một cổng thanh toán không còn dùng.
3. *Bỏ chặng kiểm tra migration khỏi CI* — mất cơ chế phát hiện đúng loại lỗi này
   về sau.

**Quyết định.** Chọn 1. File `core/migrations/0005_remove_cartorder_stripe_payment_intent.py`
do `makemigrations` sinh, chạy với `grocerly.settings_test` (không kết nối database nào).

**Lý do.** Stripe đã được thay bằng VNPay từ TLCN; cột thừa là nợ kỹ thuật, và chặng
kiểm tra migration chỉ có ý nghĩa nếu nó xanh ngay từ lần chạy đầu.

**Hệ quả.**
- Chưa `migrate` lên database nào. Migration được áp khi dựng database KLTN (P-11);
  không chạy lên database TLCN (D-002).
- Không phải sửa đặc tả: `SRS.md` và `SDD.md` không nhắc tới trường này (đã kiểm
  17/09/2026).

---

## D-021 · Không lưu báo cáo tuần trong repo

- **Ngày:** 21/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** Mỗi tuần có hai bản báo cáo cùng nội dung: thư mục
`docs/weekly_report/` trong repo và bản đã nộp trên portal projects-fit.hcmute.edu.vn.
Bản trên portal mới là bản chính thức — có dấu thời gian nộp và có ý kiến GVHD ghi
ngay dưới đó. Rubric cũng đo tần suất báo cáo theo sổ theo dõi của GVHD, và chỉ đòi
repository có **đầy đủ lịch sử commit**, không đòi file báo cáo.

**Phương án đã cân nhắc**

1. *Giữ nguyên* — hai nguồn sự thật cho cùng một nội dung, phải đồng bộ tay mỗi tuần.
2. *Rút gọn từng file, vẫn commit* — ngắn hơn nhưng vẫn còn hai bản.
3. *Gitignore cả thư mục* — portal là bản duy nhất.

**Quyết định.** Chọn (3). Thêm `docs/weekly_report/` vào `.gitignore` và gỡ thư mục
khỏi vùng theo dõi. Thư mục vẫn dùng để soạn thảo trên máy, chỉ không commit; nội
dung cũ vẫn còn trong lịch sử Git.

**Lý do.** Rút gọn và làm sạch repo. Báo cáo đã nộp trên portal của trường rồi nên
giữ thêm một bản trong repo không thêm minh chứng nào, chỉ thêm việc đồng bộ.

**Hệ quả.**
- Lịch 15 tuần và hạn nộp từng tuần chuyển sang [`PLAN.md`](PLAN.md) §2.
- Quy ước viết văn bản nộp cho GVHD chuyển sang `AGENTS.md`/`CLAUDE.md` §3.
- Phần tóm tắt dán lên portal bỏ link "Báo cáo đầy đủ trên GitHub" — không còn
  file để trỏ tới, nên ô *Nội dung* phải tự đứng vững một mình.
- Tuần nào chỉ có mỗi việc viết báo cáo thì tuần đó không có commit. Rubric đòi
  ≥ 90% số tuần có commit cho Mức 5, nên vẫn phải có việc thật mỗi tuần.
- Đề cương KLTN (`DE_CUONG.md`) chuyển vào chính thư mục này cùng ngày, vì cùng một
  lý do: bản GVHD đọc là bản DOCX/PDF đã nộp trên portal, giữ thêm bản Markdown trong
  repo chỉ tạo ra nguồn thứ hai phải đồng bộ. [`COMMITMENT.md`](COMMITMENT.md) thì
  **ở lại** repo — §3 của nó định nghĩa các mã L-x mà test (`xfail`), `pytest.ini` và
  §8 của `AGENTS.md`/`CLAUDE.md` đang trỏ tới.
- Không ảnh hưởng D-001: đặc tả, kế hoạch và quyết định vẫn nằm trong repo.

---

## D-022 · Giá của giỏ hàng luôn đọc lại từ database, không tin giá trình duyệt gửi

- **Ngày:** 21/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** L-6 trong [`COMMITMENT.md`](COMMITMENT.md): trang sản phẩm gọi
`/add-to-cart/` kèm tham số `price`, và server lưu thẳng con số đó vào session.
`save_checkout_info` cộng tổng đơn hàng từ chính con số đó rồi gửi sang VNPay.
Khách sửa tham số trên URL là đặt được hàng với giá bất kỳ. Tiền lại tính bằng
`float`, trái với quy ước dùng `Decimal` của đồ án.

Không bỏ được tham số `price` khỏi request, vì cả trang sản phẩm lẫn trợ lý AI đều
đang gửi nó; giỏ hàng lại nằm trong session nên còn những session cũ đang mang giá
kiểu `float`.

**Phương án đã cân nhắc**

1. *Chỉ kiểm tra lúc tạo đơn* — so giá trong session với `Product.price`, lệch thì
   báo lỗi. Ít chạm code, nhưng giỏ hàng vẫn hiện giá sai cho tới lúc thanh toán,
   và phải nghĩ ra thông báo lỗi cho tình huống người dùng thật không bao giờ gặp.
2. *Bỏ hẳn giá khỏi session, cần thì truy vấn lại* — sạch nhất, nhưng template giỏ
   hàng và mini-cart đang đọc `item.price` từ session, nên phải sửa cả bốn view lẫn
   ba template.
3. *Giữ giá trong session nhưng coi nó là bản sao của database* — mỗi lần đụng tới
   giỏ thì ghi đè lại bằng giá hiện tại trong `Product`.

**Quyết định.** Chọn (3). Thêm `_refresh_cart(request)` trong `core/views.py`: hàm
này ghi đè giá của từng dòng giỏ bằng `Product.price`, bỏ dòng nào không còn sản
phẩm, và trả về tổng tiền kiểu `Decimal`. Bốn view giỏ hàng cùng
`save_checkout_info` đều gọi nó. `add_to_cart` tra sản phẩm theo `id`, không thấy
thì trả 404, và dựng dòng giỏ hoàn toàn từ bản ghi `Product` — tên, giá lẫn ảnh.
Sau đó `/add-to-cart/` chỉ còn nhận hai tham số: `id` và `qty`.

**Lý do.** Cách này bịt lỗ hổng ở đúng một chỗ thay vì rải kiểm tra khắp nơi: sau
khi `_refresh_cart` chạy thì mọi con số phía sau nó đã là giá của hệ thống, nên
`save_checkout_info` không cần biết gì về chuyện chống giả mạo. Nó cũng gộp luôn
bốn vòng lặp cộng tổng giống hệt nhau đang nằm rải trong `core/views.py`. Giá vẫn
nằm trong session nên template và JavaScript không phải sửa.

**Hệ quả.**
- Giá trong session đổi từ số `float` sang chuỗi thập phân, ví dụ `"25000.00"` —
  session lưu bằng JSON nên không chứa được `Decimal`. Bộ lọc `vnd`, `mul` và hàm
  `formatVnd` đều đã nhận chuỗi, nên giao diện không đổi; session cũ tự chuẩn hóa
  ở lần đụng tới giỏ kế tiếp.
- Sản phẩm bị xóa mềm hoặc gỡ bán trong lúc khách còn để trong giỏ thì dòng đó biến
  mất khỏi giỏ. Đây là hành vi mới với người dùng — đã ghi vào [`SRS.md`](SRS.md) §6.1.
- Hai đoạn JavaScript gọi `/add-to-cart/` trong `partials/base.html` (nút Thêm vào
  giỏ và nút xác nhận của trợ lý AI) bỏ gửi `price`, `title`, `pid`, `image` — server
  không đọc tới nữa. Kéo theo đó, bốn `<input type="hidden">` chỉ tồn tại để nuôi
  đoạn JS này được xóa khỏi 5 template (`index.html`, `product-detail.html`,
  `wishlist.html`, `async/product-list.html`, `async/wishlist-list.html`); hai input
  còn lại là `product-id-` và `product-quantity-`. Xóa luôn đoạn chuẩn hóa chuỗi giá
  kiểu `120.000` và mấy dòng `console.log` trong handler, vì không còn giá để gửi.
- `safe_float` giờ chỉ còn `safe_int` gọi tới. Giữ nguyên vì nó vẫn là chỗ xử lý
  chuỗi số kiểu `120.000` gửi lên từ trình duyệt.
- L-7 (không kiểm tồn kho) sẽ sửa ngay trong `_refresh_cart` — cùng một chỗ đã nắm
  sẵn cả dòng giỏ lẫn bản ghi `Product`.

---

## D-023 · Chỉ VNPay mới xác nhận được đơn đã thanh toán

- **Ngày:** 21/09/2026
- **Trạng thái:** Đã chốt

**Bối cảnh.** L-8 trong [`COMMITMENT.md`](COMMITMENT.md): `payment_completed_view`
tự đặt `paid_status = True` cho mọi đơn `online` còn chưa thanh toán. Đây là trang
mà `vnpay_return` chuyển tới sau khi thanh toán xong, nhưng nó không kiểm tra gì
cả — khách đặt hàng xong rồi mở thẳng `/payment-completed/<oid>/` là đơn thành đã
thanh toán mà chưa trả đồng nào. Cùng kiểu lỗi với L-6: tin vào thứ trình duyệt
gửi lên thay vì tin vào nguồn dữ liệu của hệ thống.

Hai chỗ đổi `paid_status` một cách hợp lệ là `vnpay_return` và `vnpay_ipn`, cả hai
đều gọi `validate_response` để kiểm chữ ký HMAC trước.

**Phương án đã cân nhắc**

1. *Chỉ bỏ hai dòng gán `paid_status`* — đúng phần lỗ hổng, nhưng template
   `payment-completed.html` vẫn in "Payment Completed" cho mọi đơn không phải COD,
   nên đơn chưa trả tiền vẫn được báo là thanh toán xong.
2. *Bỏ hai dòng gán, rồi sửa template hiển thị theo `paid_status`* — thành ba trạng
   thái phải viết chữ cho cả hai bản dịch, trong khi đơn chưa thanh toán thì việc
   cần làm là quay lại trả tiền chứ không phải đọc thông báo.
3. *Bỏ hai dòng gán, và đưa đơn online chưa thanh toán về trang thanh toán.*

**Quyết định.** Chọn (3). `payment_completed_view` không còn ghi vào `paid_status`;
đơn `online` mà `paid_status` còn `False` thì view đẩy về `core:checkout` kèm
`messages.warning` nhắc thanh toán. Đơn COD vẫn vào được trang hoàn tất với
`paid_status = False`, vì COD trả tiền khi nhận hàng.

**Lý do.** Cách này để việc xác nhận thanh toán nằm đúng ở hai view đã kiểm chữ ký,
đúng như mô tả luồng VNPay trong [`SDD.md`](SDD.md). Nó cũng không đẻ thêm màn hình
mới: `core:checkout` sẵn có nút thanh toán lại, và bản thân view đó đã tự đẩy đơn
đã thanh toán ngược về trang hoàn tất nên không có vòng lặp chuyển hướng.

**Hệ quả.**
- Đơn online chưa thanh toán không còn bị xóa giỏ hàng trong session, vì view thoát
  ra trước đoạn dọn session. Khách bỏ dở lần thanh toán vẫn giữ nguyên giỏ.
- Test `test_payment_completed_page_does_not_mark_unpaid_order_as_paid` đã gỡ
  `xfail`; thêm hai test cho hai lối vào hợp lệ của trang này — đơn online đã được
  VNPay xác nhận, và đơn COD chưa thanh toán.
- `vnpay_ipn` vẫn trả `RspCode 00` cho giao dịch thất bại. Đây là chỗ đáng xem lại
  nhưng không thuộc L-8, chưa sửa trong lần này.

---

<!--
Mẫu cho quyết định mới — sao chép xuống dưới cùng:

## D-00x · <Tiêu đề ngắn, ở thể khẳng định>

- **Ngày:** DD/MM/YYYY
- **Trạng thái:** Đề xuất | Đã chốt | Thay thế bởi D-0yy

**Bối cảnh.** Điều gì buộc phải ra quyết định lúc này?

**Phương án đã cân nhắc**
1. *Phương án A* — đánh đổi gì.
2. *Phương án B* — đánh đổi gì.

**Quyết định.** Chọn phương án nào.

**Lý do.** Vì sao đánh đổi đó chấp nhận được với đề tài này.

**Hệ quả.** Việc gì phát sinh sau quyết định này.
-->
