# Báo cáo tiến độ hằng tuần

Thư mục chứa báo cáo tiến độ gửi GVHD, mỗi tuần một file.

## Quy ước đặt tên file

```
tuan-NN.md
```

`NN` là số tuần có đệm số 0: `tuan-01.md` → `tuan-15.md`.

Đệm số 0 để file tự sắp đúng thứ tự trong thư mục — không có nó thì `tuan-10`
sẽ nhảy lên trước `tuan-2`. Khoảng ngày của mỗi tuần nằm trong header của chính
báo cáo và trong bảng dưới đây, nên không cần lặp lại ở tên file.

## Lịch 15 tuần

| Tuần | Từ | Đến | File |
|---|---|---|---|
| 1 | 07/09/2026 | 13/09/2026 | `tuan-01.md` |
| 2 | 14/09/2026 | 20/09/2026 | `tuan-02.md` |
| 3 | 21/09/2026 | 27/09/2026 | `tuan-03.md` |
| 4 | 28/09/2026 | 04/10/2026 | `tuan-04.md` |
| 5 | 05/10/2026 | 11/10/2026 | `tuan-05.md` |
| 6 | 12/10/2026 | 18/10/2026 | `tuan-06.md` |
| **7** | **19/10/2026** | **25/10/2026** | `tuan-07.md` — **hạn chốt cam kết sản phẩm + metric** |
| 8 | 26/10/2026 | 01/11/2026 | `tuan-08.md` |
| 9 | 02/11/2026 | 08/11/2026 | `tuan-09.md` |
| 10 | 09/11/2026 | 15/11/2026 | `tuan-10.md` |
| 11 | 16/11/2026 | 22/11/2026 | `tuan-11.md` |
| 12 | 23/11/2026 | 29/11/2026 | `tuan-12.md` |
| 13 | 30/11/2026 | 06/12/2026 | `tuan-13.md` |
| 14 | 07/12/2026 | 13/12/2026 | `tuan-14.md` |
| 15 | 14/12/2026 | 20/12/2026 | `tuan-15.md` |

## Cách làm

- Sao chép [`_TEMPLATE.md`](_TEMPLATE.md), đổi tên theo bảng trên rồi điền.
  File mẫu bắt đầu bằng `_` nên không bị nhầm là báo cáo thật.
- **Tần suất:** ≥ 1 lần/tuần, kể cả tuần làm được ít. Tuần bận thì viết báo cáo
  ngắn — bỏ hẳn mới là vấn đề.
- **Commit ngay trong tuần đó**, đừng viết dồn nhiều tuần vào cuối kỳ.

## Vì sao phải làm

Rubric KLTN yêu cầu báo cáo tiến độ **≥ 1 lần/tuần** với GVHD, có ghi nhận nội
dung đã làm, vướng mắc và kế hoạch tuần kế tiếp. Ba hệ quả cụ thể:

- Tần suất dưới **0,5 lần/tuần** → gate **G2** → TC2.2 và TC2.4 mỗi tiêu chí bị
  hạ một mức.
- Sổ theo dõi tiến độ là hồ sơ minh chứng bắt buộc (Mục 8 của rubric). Thiếu nó,
  các tiêu chí liên quan không được xếp từ Mức 4 trở lên.
- Ngưỡng Mức 5 là **≥ 1,0 lần/tuần** — với 15 tuần thì gần như tuần nào cũng phải
  có, không có cách nào bù lại về sau.

Ngoài điểm số, các báo cáo này còn là nguồn để viết chương thực nghiệm và để trả
lời hội đồng: chúng ghi lại *tại thời điểm đó* mình đã nghĩ gì và vì sao chọn
hướng đó — thứ mà vài tháng sau không ai nhớ chính xác nữa.

## Liên kết

- Kế hoạch và backlog: [`../PLAN.md`](../PLAN.md)
- Quyết định quan trọng: [`../DECISIONS.md`](../DECISIONS.md)
- Đặc tả yêu cầu: [`../SRS.md`](../SRS.md)
- Nhật ký dùng AI: [`../AI_USAGE_LOG.md`](../AI_USAGE_LOG.md)
