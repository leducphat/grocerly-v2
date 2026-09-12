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
