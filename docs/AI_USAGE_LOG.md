# AI USAGE LOG — Grocerly (KLTN)

Nhật ký sử dụng LLM / Agentic AI trong quá trình làm đồ án.

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| Bắt đầu ghi | 10/09/2026 |
| Phục vụ tiêu chí | TC2.3 (5 điểm) — *Mức độ làm chủ và năng lực kiểm soát khi sử dụng LLM / Agentic AI* |

---

## Vì sao có file này

Rubric KLTN nói rõ: **dùng AI không bị trừ điểm**. Thứ bị chấm là mức độ sinh viên
làm chủ sản phẩm. Cụ thể:

- Không nộp nhật ký này (và cũng không nộp bản cam kết không dùng AI) → gate **G3**
  → TC2.3 bị chặn ở **2,75/5**.
- Nội dung kê khai mâu thuẫn với lịch sử Git hoặc với phần trả lời vấn đáp → gate
  **G4** → TC2.3 = **0 điểm**, đồng thời kích hoạt quy trình xác định đạo văn.
- Ngưỡng Mức 5: nhật ký **đối chiếu được với lịch sử commit**, giải thích đúng
  **100%** vị trí mã do AI sinh khi hội đồng chọn ngẫu nhiên ≥ 5 chỗ, và nêu được
  **≥ 5 lỗi/ảo giác của AI đã tự phát hiện** kèm phân tích nguyên nhân và commit sửa.

Nói cách khác: file này không phải thủ tục hành chính. Nó là bằng chứng cho câu
"em hiểu code của em", và nó chỉ có giá trị nếu được ghi *ngay khi làm*, vì mỗi
dòng phải khớp với một commit có thật.

## Quy ước ghi

- Ghi **ngay sau mỗi phiên làm việc có dùng AI**, không dồn.
- Mỗi dòng phải gắn được với commit tương ứng — chưa commit thì ghi
  `*(chưa commit)*` rồi cập nhật lại sau.
- **Không dán secret, khóa API, chuỗi kết nối hay dữ liệu người dùng thật vào
  prompt** — và cũng không dán chúng vào file này.
- Ghi trung thực phần nào do AI sinh, phần nào do sinh viên tự viết hoặc sửa lại.

---

## 1. Nhật ký phiên làm việc

| Ngày | Công cụ | Phạm vi | Prompt chính | AI sinh ra | SV tự viết / sửa lại | Commit |
|---|---|---|---|---|---|---|
| 10/09/2026 | Claude Code (Opus 5) | Đọc rubric KLTN; rà soát repo đối chiếu rubric; dựng khung tài liệu theo Spec Driven Development | "Đọc project + báo cáo TLCN để nắm context"; "đọc rubric mới nhất của KLTN"; "theo Spec Driven Development, tạo CLAUDE.md, AGENTS.md, docs/ chứa PLAN/DECISIONS/PRD + weekly_report" | **Toàn bộ** nội dung `AGENTS.md`, `CLAUDE.md`, `docs/SRS.md`, `docs/PLAN.md`, `docs/DECISIONS.md` (D-001→D-010), `docs/weekly_report/README.md` + `_TEMPLATE.md`, và chính file này. Xóa `.github/copilot-instructions.md`. | SV định hướng và bác bỏ nhiều đề xuất của AI trong phiên (xem §2), chưa tự viết lại nội dung | *(chưa commit)* |
| 10/09/2026 | Claude Code (Opus 5) | Điều chỉnh backlog `PLAN.md`; hỏi rubric về P-03 (bản cam kết) và P-06 (PR khi làm một mình) | "sửa P-01 là Khung specs; P-03 là gì, ở đâu trong rubric; P-06 làm một mình có cần branch rồi PR không"; "gộp viết AC vào rà soát đặc tả TLCN, tách SRS/SDD ngay từ đầu, khảo sát 2–3 người không chắc nổi"; "ghép P-22 vào P-25" | Sửa `PLAN.md` (P-01, P-03, P-06, thêm P-07, gộp P-20 vào P-23, gộp P-22 vào P-25, bỏ P-27); thêm D-011, D-012, D-013 vào `DECISIONS.md`; sửa ghi chú ranh giới ở đầu `SRS.md`. AI đọc nguyên văn rubric trên Google Drive để trích dẫn; AI đề xuất phương án ghép khảo sát vào thực nghiệm | SV quyết định: vẫn chia nhánh + tự PR; gộp AC vào rà soát; tách SRS/SDD sớm (bác bỏ D-010 của AI); chọn ghép khảo sát vào P-25 | *(chưa commit)* |

---

## 2. Lỗi / ảo giác của AI đã phát hiện

Mức 5 cần **≥ 5 mục** kèm phân tích nguyên nhân và commit sửa. Hiện có: **8**.

| # | Ngày | Lỗi | Nguyên nhân | Ai phát hiện | Commit sửa |
|---|---|---|---|---|---|
| 1 | 10/09/2026 | AI viết `AGENTS.md` / `CLAUDE.md` bằng tiếng Anh trong khi `docs/` viết tiếng Việt | AI áp mặc định "tài liệu kỹ thuật thì viết tiếng Anh" thay vì theo ngữ cảnh đồ án tiếng Việt đã thiết lập | SV | *(chưa commit)* |
| 2 | 10/09/2026 | AI thiết kế `CLAUDE.md` chỉ là con trỏ tới `AGENTS.md` (D-003) | AI tối ưu cho mục tiêu "tránh trùng lặp" mà không hỏi yêu cầu thật; kết quả là `CLAUDE.md` đọc một mình thì vô nghĩa | SV | *(chưa commit)* — thay bằng D-006 |
| 3 | 10/09/2026 | AI chốt đặc tả TLCN là "baseline đóng băng", chỉ cho ghi delta (D-004) | AI giả định báo cáo đã chấm điểm thì bất biến, bỏ qua khả năng chính đặc tả đó có chỗ sai/lỗi thời | SV | *(chưa commit)* — thay bằng D-007 |
| 4 | 10/09/2026 | Script kiểm tra link Markdown báo 4 link "GÃY" trong khi cả 4 đều tồn tại | Regex cắt chuỗi không loại bỏ dấu `)` cuối, làm tên file thành `PLAN.md)` — lỗi false positive, suýt dẫn tới "sửa" thứ không hỏng | AI (tự phát hiện khi đối chiếu với `ls`) | *(chưa commit)* |
| 5 | 10/09/2026 | AI đặt tên tài liệu đặc tả là `PRD.md` | AI dùng thuật ngữ phổ biến trong ngành phần mềm thương mại, không đối chiếu Mục 8 của rubric — nơi gọi đích danh hồ sơ là "SRS/SDD" | SV | *(chưa commit)* — xem D-009 |
| 6 | 10/09/2026 | AI đặt tên P-01 là "Khung SDD" trong khi chính AI dùng "SDD" cho tài liệu thiết kế `SDD.md` (D-010) | AI dùng một từ viết tắt cho hai nghĩa (Spec Driven Development và Software Design Document) mà không kiểm tra xung đột trong cùng bộ tài liệu | SV | *(chưa commit)* — đổi thành "Khung specs" |
| 7 | 10/09/2026 | AI chốt hoãn tách SRS/SDD tới sau P-24 (D-010) | AI chỉ cân nhắc công sức tách file, bỏ qua việc tách muộn làm lịch sử Git của phần thiết kế bị cắt ở ngày tách — mất dấu vết quá trình rà soát, vốn là minh chứng rubric chấm | SV | *(chưa commit)* — thay bằng D-011 |
| 8 | 10/09/2026 | AI tách "viết acceptance criteria" (P-20) và "rà soát đặc tả TLCN" (P-23) thành hai việc riêng | AI chia việc theo loại sản phẩm đầu ra thay vì theo cách làm thực tế: cả hai đều phải đi qua cùng 26 use case, tách ra là rà hai lượt | SV | *(chưa commit)* — gộp vào P-23 |

**Ghi chú khi bảo vệ:** bảy trong tám mục trên do sinh viên phát hiện, không phải
AI tự sửa. Đó là điểm cần nói thẳng — nó cho thấy vai trò kiểm soát nằm ở người,
đúng tinh thần TC2.3.

---

## 3. Quy trình kiểm soát đầu ra AI

Mức 5 yêu cầu việc kiểm soát phải **thành hệ thống**, không phải "chạy thử thấy
được thì thôi". Checklist áp dụng cho mọi output của AI trước khi commit:

- [ ] **Đọc hết** phần AI sinh ra. Không commit thứ chưa đọc.
- [ ] **Đối chiếu tài liệu chính thức** (Django docs, docs của thư viện, rubric)
      thay vì tin lời AI — đặc biệt với tên API, tham số, và con số ngưỡng.
- [ ] **Chạy test và linter**, không chỉ chạy thử bằng tay.
- [ ] **Kiểm tra prompt không chứa** secret, khóa API, chuỗi kết nối, dữ liệu
      người dùng thật.
- [ ] **Kiểm tra giấy phép** nếu AI đề xuất chép đoạn mã hoặc thêm thư viện ngoài.
- [ ] **Câu hỏi cuối cùng:** *nếu hội đồng chỉ vào đúng dòng này và cho 3 phút,
      mình có giải thích được nó làm gì, vì sao có mặt ở đây, và bỏ đi thì hệ
      thống hỏng chỗ nào không?* Nếu không → chưa được commit.

---

## Liên kết

- Kế hoạch và backlog: [`PLAN.md`](PLAN.md) — P-04
- Quyết định quan trọng: [`DECISIONS.md`](DECISIONS.md)
- Đặc tả yêu cầu: [`SRS.md`](SRS.md)
- Báo cáo tuần: [`weekly_report/`](weekly_report/)
