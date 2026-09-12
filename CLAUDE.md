# CLAUDE.md — Grocerly (KLTN)

> **⚠️ File song sinh.** `AGENTS.md` và `CLAUDE.md` có nội dung **giống hệt nhau
> từ dòng 2 trở đi**; chỉ khác nhau ở dòng tiêu đề. Mỗi file phải tự đứng vững —
> đọc một file là đủ, không cần mở file kia.
>
> **Sửa một file thì phải sửa file còn lại trong cùng một commit.** Kiểm tra:
> ```bash
> diff <(tail -n +2 AGENTS.md) <(tail -n +2 CLAUDE.md)   # phải không in ra gì
> ```

---

## 1. Dự án này là gì

**Grocerly** — website thương mại điện tử bán thực phẩm, tích hợp trợ lý AI có
khả năng tìm sản phẩm, thêm vào giỏ và dẫn người dùng tới thanh toán qua hội
thoại ngôn ngữ tự nhiên.

Đây là codebase của **Khóa luận tốt nghiệp (KLTN)** tại Trường ĐH Công nghệ Kỹ
thuật TP.HCM, Khoa CNTT, ngành Công nghệ Phần mềm. Đồ án kế thừa một **Tiểu luận
chuyên ngành (TLCN)** cùng đề tài, cùng GVHD, đã nộp và đã có điểm.

| | |
|---|---|
| Sinh viên | Lê Đức Phát — 21139083 |
| GVHD | Hoàng Văn Dũng |
| GV phản biện | Hoàng Thái Xuân Khoa |

**Tài liệu điều hướng:**

| Câu hỏi | File |
|---|---|
| Sản phẩm phải làm được gì? | [`docs/SRS.md`](docs/SRS.md) |
| Hệ thống được xây thế nào? | [`docs/SDD.md`](docs/SDD.md) |
| Sắp làm gì, đang tới đâu? | [`docs/PLAN.md`](docs/PLAN.md) |
| Vì sao lại làm theo cách này? | [`docs/DECISIONS.md`](docs/DECISIONS.md) |
| Đã báo cáo gì với GVHD? | [`docs/weekly_report/`](docs/weekly_report/) |
| AI đã sinh ra phần nào? | [`docs/AI_USAGE_LOG.md`](docs/AI_USAGE_LOG.md) |

---

## 2. Lịch KLTN

Đồ án chạy **15 tuần**, đánh số **Tuần 1 → Tuần 15**; mỗi tuần bắt đầu Thứ Hai.

| Mốc | Tuần | Ngày |
|---|---|---|
| Bắt đầu | Tuần 1 | 07/09/2026 – 13/09/2026 |
| **Hạn chốt cam kết sản phẩm + bộ metric** | **hết Tuần 7** | **25/10/2026** — mốc 50% thời gian |
| Kết thúc | Tuần 15 | 14/12/2026 – 20/12/2026 |
| Phản biện | — | Dự kiến tháng 12/2026 |

Lịch đầy đủ 15 tuần: [`docs/weekly_report/README.md`](docs/weekly_report/README.md).

Mốc 50% là **điều kiện cứng**: không chốt được bản cam kết đúng hạn thì đồ án
*không đủ điều kiện bảo vệ* (xem §4).

**Nhịp bắt buộc:** báo cáo tiến độ với GVHD ≥ 1 lần/tuần, ghi vào
`docs/weekly_report/`. Với đồ án 15 tuần, Mức 5 của rubric đòi **≥ 14/15 tuần có
commit** — nghĩa là làm đều, không dồn.

---

## 3. Cách làm việc: Spec Driven Development

Đặc tả dẫn đường, code theo sau. Với mọi thay đổi không tầm thường:

1. **Đặc tả trước.** Nếu thay đổi làm khác đi hành vi mà người dùng nhìn thấy,
   cập nhật `docs/SRS.md` (yêu cầu + acceptance criteria) *trước khi* viết code.
2. **Ghi lại quyết định.** Bất cứ lựa chọn nào có phương án thay thế hợp lý — thư
   viện, thay đổi schema, kiến trúc — đều phải có một mục trong
   `docs/DECISIONS.md` kèm bối cảnh, các phương án đã cân nhắc và lý do chọn.
   Thay đổi chạm tới mô hình dữ liệu, giao diện hay kiến trúc thì cập nhật cả
   `docs/SDD.md`.
3. **Đưa vào kế hoạch.** Chia việc thành các mục theo dõi được trong `docs/PLAN.md`.
4. **Viết test kèm theo** (xem §8).
5. **Báo cáo tuần** trong `docs/weekly_report/`.

**`SRS.md` và `SDD.md` là tài liệu sống, không phải văn bản đóng băng.** Đặc tả
TLCN có thể có chỗ sai hoặc đã lỗi thời so với mã nguồn hiện tại. Khi phát hiện,
sửa file tương ứng cho đúng thực tế và ghi lại việc sửa đó trong `docs/PLAN.md`
§6 — đừng im lặng sửa, cũng đừng để đặc tả sai tồn tại vì "báo cáo cũ viết vậy".

---

## 4. Ràng buộc chấm điểm chi phối cách làm

Rubric KLTN (link trong `docs/DECISIONS.md` D-001) chấm theo **minh chứng**. Ba hệ
quả ràng buộc mọi agent làm việc trên repo này:

**(a) Mọi thứ phải giải thích được.** Theo rubric, bất kỳ nội dung nào — code, sơ
đồ, hay chữ trong báo cáo — mà sinh viên không giải thích được tại buổi bảo vệ đều
bị tính là đạo văn, *bất kể do AI hay do người viết*. Hai chỗ không giải thích
được là toàn bộ đồ án 0 điểm.

> **Vì vậy: không sinh ra code mà sinh viên không yêu cầu và không theo nổi.**
> Chọn cách cài đặt đơn giản, dễ đọc thay vì cách thông minh nhưng khó giải thích.
> Chỗ nào không hiển nhiên thì giải thích trong comment hoặc trong `DECISIONS.md`.

**(b) Việc dùng AI phải được ghi log.** Dùng AI được phép và không bị trừ điểm,
nhưng phải có AI Usage Log đối chiếu được với lịch sử Git: công cụ nào, phạm vi
gì, prompt chính, AI sinh ra phần nào, sinh viên sửa phần nào. Thiếu log thì tiêu
chí đó bị chặn ở 2,75/5. Ghi vào `docs/AI_USAGE_LOG.md` **ngay sau mỗi phiên**,
nêu rõ phần nào do AI sinh, kèm cả những lỗi/ảo giác của AI đã phát hiện — Mức 5
cần ≥ 5 lỗi có phân tích nguyên nhân.

**(c) Minh chứng quá trình không back-fill được.** Tỉ lệ tuần có commit, lịch sử
chạy CI, số lần deploy, báo cáo tuần — tất cả đều tích lũy theo thời gian. Việc
nào sinh ra loại minh chứng này thì làm sớm, đừng để cuối kỳ.

---

## 5. Phạm vi KLTN

Trọng tâm là **làm chắc phần cốt lõi đã có**, không chạy theo tính năng mới:

- Chuyên nghiệp hóa kỹ thuật phần mềm — kiểm thử tự động, CI/CD, quản lý chất
  lượng mã nguồn, thực nghiệm người dùng thật.
- Hoàn thiện đặc tả và tài liệu thiết kế cho khớp mã nguồn.
- Sửa các chỗ sai/lỗi thời trong đặc tả TLCN.

Các ý tưởng mở rộng (tìm kiếm full-text, live chat thời gian thực, gợi ý bằng
Machine Learning, mobile app, mô hình nhiều người bán — D-015) **không thuộc phạm
vi KLTN**; chúng thuộc mục "Các
hướng phát triển mở rộng" ở cuối báo cáo. Đừng tự ý bắt tay làm chúng.

---

## 6. Cấu trúc repository

```
grocerly-ecom/
├── AGENTS.md, CLAUDE.md      # hướng dẫn agent (hai bản song sinh)
├── docs/                     # SRS, SDD, PLAN, DECISIONS, AI_USAGE_LOG, weekly_report
└── grocerly/                 # thư mục gốc Django — manage.py nằm ở ĐÂY
    ├── grocerly/             # settings, urls gốc, wsgi/asgi, middleware
    ├── core/                 # catalog, giỏ hàng, đơn hàng, checkout, VNPay, đánh giá
    ├── userauths/            # User tùy biến (đăng nhập bằng email), Profile, ContactUs
    ├── useradmin/            # dashboard nhân viên cửa hàng (khác Django admin)
    ├── store_api/            # DRF endpoints + chat AI Gemini  (/api/v1/)
    ├── templates/            # core/, userauths/, useradmin/, partials/
    ├── static/, media/, locale/   # assets, file upload, bản dịch vi+en
    └── requirements.txt, .env, .env.example
```

**Mọi lệnh `manage.py` chạy từ trong `grocerly/`, không phải từ gốc repo.**

---

## 7. Quy ước code — những điểm này có ràng buộc thật

| Hạng mục | Quy tắc |
|---|---|
| **Định danh trên URL** | Dùng ShortUUID (`c_id`, `v_id`, `p_id`, `sku`, `oid`), không dùng khóa chính số. |
| **User model** | Tùy biến, `USERNAME_FIELD` là email. Luôn dùng `settings.AUTH_USER_MODEL` hoặc `get_user_model()` — **không** import `django.contrib.auth.models.User`. |
| **Tiền tệ** | `DecimalField(max_digits=20, decimal_places=2)`, đơn vị VND. Không dùng float. |
| **Xóa dữ liệu** | `Category`, `Vendor`, `Product`, `Coupon` kế thừa `SoftDeleteModel`. Manager mặc định ẩn bản ghi đã xóa mềm; muốn thấy thì dùng `all_objects`. Không thêm hard delete cho các model này. |
| **View** | `core` và `useradmin` dùng function-based view; `store_api` dùng DRF. Giữ nguyên phong cách sẵn có trừ khi có quyết định trong `DECISIONS.md` nói khác. |
| **URL / i18n** | Route trang được bọc trong `i18n_patterns` → có tiền tố `/vi/` hoặc `/en/`. API tại `/api/v1/` **cố ý nằm ngoài** i18n. Nhớ tính tiền tố này khi redirect và khi viết test. |
| **Định tuyến staff** | `RestrictStaffMiddleware` giới hạn staff/superuser trong một danh sách tiền tố URL cho phép. Thêm route cho staff thì phải cập nhật danh sách đó. |
| **Template** | `core.context_processors.default` đã bơm `categories` vào mọi template — không truy vấn lại danh mục trong từng view. |
| **Chuỗi hiển thị** | Bọc bằng `gettext_lazy as _`, cập nhật cả `locale/vi` lẫn `locale/en`. Ngôn ngữ mặc định bị ép về `vi`. |
| **Media** | `USE_CLOUDINARY=True` chuyển storage sang Cloudinary; ngược lại dùng `media/` cục bộ. Code phải chạy được ở cả hai chế độ. |
| **Secret** | Cấu hình chỉ qua biến môi trường. `.env` đang được gitignore và phải giữ nguyên như vậy. Không hardcode key, không in key ra log, commit hay báo cáo. |

**Ngôn ngữ:** trao đổi với sinh viên bằng tiếng Việt. Tài liệu trong `docs/` và hai
file hướng dẫn này viết tiếng Việt. Code, tên biến, tên hàm và commit message viết
tiếng Anh. Chuỗi hiển thị cho người dùng đi qua `gettext_lazy` với đủ hai bản dịch.

---

## 8. Kiểm thử

Rubric yêu cầu kiểm thử tự động kèm báo cáo độ phủ; hiện tại **chưa có test nào**
(cả bốn `tests.py` đều là stub). Khi viết test:

- Framework: **pytest + pytest-django**, đặt trong `tests/` của từng app.
- Mỗi test theo cấu trúc Arrange–Act–Assert, tên test nói rõ hành vi được kiểm —
  ví dụ `test_add_to_cart_rejects_quantity_above_stock`.
- Phủ cả ca âm và ca biên, không chỉ luồng thuận lợi — rubric yêu cầu rõ điều này.
- Mỗi test nên truy vết được về một acceptance criteria trong `docs/SRS.md`.

---

## 9. Lệnh thường dùng

```bash
cd grocerly

python manage.py runserver          # chạy dev server
python manage.py migrate            # áp dụng migration
python manage.py makemigrations     # sau khi đổi model
python manage.py createsuperuser    # tạo tài khoản quản trị
python manage.py collectstatic      # trước khi deploy

django-admin makemessages -l vi -l en   # trích chuỗi i18n
django-admin compilemessages            # biên dịch .po -> .mo
```

---

## 10. Biến môi trường

`grocerly/.env` chi phối cấu hình. Các key mà `settings.py` đọc:

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL` (hoặc
nhóm `POSTGRES_*`), `USE_CLOUDINARY`, `CLOUDINARY_URL`, `GEMINI_API_KEY`,
`VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`, `VNPAY_PAYMENT_URL`, `VNPAY_API_URL`,
`STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`.

Không có `DATABASE_URL` lẫn `POSTGRES_DB` thì Django tự lùi về SQLite cục bộ.

> ⚠️ **KLTN chạy trên host, database và image storage riêng.** File `.env` trong
> thư mục làm việc có thể vẫn đang trỏ tới production của TLCN. Xác nhận đúng đích
> trước mọi lệnh `migrate` hay deploy — xem `docs/DECISIONS.md` D-002.

---

## 11. Những việc không được làm

- Không commit `.env`, `db.sqlite3`, hay bất cứ thứ gì trong `media/`.
- Không chạy `migrate` lên database chưa xác nhận là của KLTN.
- Không sửa một trong hai file `AGENTS.md` / `CLAUDE.md` mà quên file kia.
- Không tự ý làm tính năng ngoài phạm vi ở §5.
- Không sinh hàng loạt code, tài liệu hay sơ đồ mà không ai đọc và sinh viên không
  bảo vệ được. Rubric không chấm khối lượng, rubric chấm mức làm chủ.
