# Grocerly

![Grocerly](https://grocerly-v2.onrender.com/static/assets/imgs/theme/logo.png)

Website bán thực phẩm của một cửa hàng, có trợ lý AI (Google Gemini) giúp khách
tìm sản phẩm, thêm vào giỏ và đi tới thanh toán bằng hội thoại. Mã nguồn khóa
luận tốt nghiệp, phát triển tiếp từ
[tiểu luận chuyên ngành](https://github.com/leducphat/grocerly-ecom).

Bản đang chạy: <https://grocerly-v2.onrender.com> (gói miễn phí, lần mở đầu có
thể mất khoảng nửa phút).

## Chức năng

Đủ các chức năng của một website thương mại điện tử thông thường, cộng thêm trợ
lý AI hỗ trợ khách mua hàng ngay trong khung chat.

- Khách: xem và lọc sản phẩm, giỏ hàng, mã giảm giá, yêu thích, đánh giá, thanh
  toán VNPay (sandbox) hoặc khi nhận hàng.
- Trợ lý AI: tìm sản phẩm, gợi ý hàng bán chạy; thêm vào giỏ và thanh toán chỉ
  chạy khi khách bấm xác nhận.
- Nhân viên cửa hàng: dashboard quản lý sản phẩm, tồn kho, đơn hàng.
- Giao diện tiếng Việt và tiếng Anh.

"Vendor" trong mã nguồn là nhà cung cấp hàng, không phải người bán.

## Công nghệ

Python 3.12, Django 5.2, Django REST Framework, PostgreSQL, Cloudinary, Google
Gemini, Bootstrap và jQuery, chạy trên Render. Kiểm thử bằng pytest và
Playwright, kiểm mã bằng ruff và jscpd.

## Chạy ở máy cá nhân

```bash
git clone https://github.com/leducphat/grocerly-v2.git
cd grocerly-v2/grocerly          # manage.py nằm ở đây
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Trong `.env`, đặt `DJANGO_DEBUG=1`, `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`,
`USE_CLOUDINARY=False` và xóa dòng `DATABASE_URL` để dùng SQLite. Trợ lý AI cần
`GEMINI_API_KEY`.

## Kiểm thử

```bash
pip install -r requirements-dev.txt
pytest --cov        # test thường, kèm độ phủ
pytest -m e2e       # test trình duyệt (cần: playwright install chromium)
ruff check .
```

Test dùng SQLite trong bộ nhớ, không đọc `.env` và không gọi dịch vụ thật. CI
trên GitHub Actions chạy các bước này cho mỗi lần push và pull request, rồi tự
deploy lên Render khi `main` có commit mới.

## Tài liệu

Đặc tả ở [`docs/SRS.md`](docs/SRS.md), thiết kế ở [`docs/SDD.md`](docs/SDD.md),
kế hoạch ở [`docs/PLAN.md`](docs/PLAN.md), các quyết định kỹ thuật ở
[`docs/DECISIONS.md`](docs/DECISIONS.md), nhật ký dùng AI ở
[`docs/AI_USAGE_LOG.md`](docs/AI_USAGE_LOG.md).

Giấy phép MIT.
