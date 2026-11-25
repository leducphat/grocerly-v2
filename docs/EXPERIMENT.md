# Kế hoạch thực nghiệm người dùng

Thiết kế buổi thực nghiệm, viết xong trước buổi đầu tiên: cách đo, kịch bản, câu
hỏi, phiếu SUS và mẫu biên bản. Lý do của từng lựa chọn ở D-065; số người theo
D-017, việc gộp phỏng vấn vào buổi thử theo D-013.

- **Lịch:** Tuần 11 (23/11 - 29/11/2026). Lỗi người thử gặp thì sửa ở Tuần 12;
  không có vòng đo lại.
- **Hình thức:** gặp trực tiếp, người thử dùng laptop của sinh viên, thử trên bản
  đang chạy tại https://grocerly-v2.onrender.com.

## 1. Đo cái gì

Ngưỡng lấy từ bản cam kết (`COMMITMENT.md` §5.2, §5.3) và không đổi sau khi đo;
đo lệch xa thì ghi vào hạn chế.

| Chỉ số | Cách tính | Ngưỡng cam kết |
|---|---|---|
| Số người thử thuộc nhóm đối tượng | Đếm theo danh sách ẩn danh | ≥ 3, nhắm 5 |
| Người thử tự đặt xong đơn (KPI) | Số người hoàn thành tác vụ 2 / số người thử | ≥ 60% |
| Thời gian tìm hàng tới đặt hàng (KPI) | Trung vị thời gian tác vụ 2 của những người hoàn thành | ≤ 5 phút |
| Tỉ lệ hoàn thành tác vụ | Số lượt tác vụ thành công / tổng số lượt (3 tác vụ x số người) | ≥ 60% |
| Điểm SUS | Trung bình điểm SUS của mọi người thử | ≥ 55 |
| Bên liên quan được phỏng vấn | Số người có biên bản phần phỏng vấn | ≥ 1, nhắm 3 |

Biên bản ghi đủ để tính cả ngưỡng tham chiếu Mức 4 của rubric (hoàn thành ≥ 80%,
SUS ≥ 68), dù không cam kết mức đó.

## 2. Người tham gia

- **Tiêu chí:** từ 18 tuổi; 3 tháng gần đây tự đặt mua thực phẩm hoặc hàng tạp hóa
  qua mạng ít nhất một lần; chưa xem hay góp ý cho dự án. Không quá một nửa là bạn
  cùng lớp; ưu tiên người đi làm, người nội trợ, sinh viên ở trọ tự nấu ăn.
- **Ẩn danh:** mã NT1, NT2... theo thứ tự buổi. Repo chỉ lưu mã, nhóm tuổi và nghề
  nghiệp chung (ví dụ "nhân viên văn phòng, 25 - 34 tuổi"). Danh sách tên thật giữ
  trên giấy, không chụp, không đưa vào repo.
- **Đồng ý:** đọc lời giới thiệu ở mục 4, chỉ bắt đầu khi người thử đồng ý. Không
  quay video, không ghi âm, người thử dừng lúc nào cũng được.

## 3. Chuẩn bị

**Một lần, trước buổi đầu:**

- Tạo trên host 5 tài khoản khách bằng trang Đăng ký, email dạng
  `nt1.grocerly@...`. Hồ sơ để trống, để người thử tự gõ thông tin giao hàng.
- In mỗi người một tờ thông tin giao hàng: họ tên "Người thử 1" (đổi số theo mã),
  địa chỉ "1 Võ Văn Ngân, phường Linh Chiểu, TP. Thủ Đức". Người thử chép từ tờ
  này, không dùng thông tin thật của mình.
- Tồn kho ngày 22/11/2026: đùi bò 23, dưa hấu 10, đủ cho 5 người. Đơn Đang xử lý
  chưa trừ kho (D-032), nên buổi trước không làm hụt hàng của buổi sau.
- In phiếu SUS (mục 7) và mẫu biên bản (mục 8), mỗi người một bộ.

**Trước mỗi buổi, khoảng 15 phút:**

1. Mở https://grocerly-v2.onrender.com/vi/ để đánh thức host (lần mở đầu có thể mất
   gần một phút), rồi mở `/api/v1/health/`, phải thấy `"status":"ok"`.
2. Gửi trợ lý một câu thử, ví dụ "có bán dưa hấu không". Trợ lý báo hết lượt hoặc
   quá tải thì dời buổi. Hai buổi cùng ngày cách nhau ít nhất một giờ, vì Gemini
   gói miễn phí giới hạn lượt theo phút và theo ngày.
3. Đăng nhập bằng tài khoản của người thử sắp tới; kiểm giỏ trống, tiếng Việt, cửa
   sổ chat đóng, trình duyệt phóng to 100%.
4. Để màn hình ở trang chủ, chuẩn bị đồng hồ bấm giờ và biên bản.

## 4. Trình tự một buổi (khoảng 20 - 25 phút)

Giới thiệu và xin đồng ý (2 phút), phỏng vấn nhu cầu (mục 5, 5 phút), ba tác vụ
(mục 6, 10 - 15 phút, người thử vừa làm vừa nói to điều mình nghĩ), phiếu SUS
(mục 7, 3 phút). Không có phần hỏi cảm nhận sau phiếu; chỗ người thử lúng túng
đã nằm trong ghi chép lúc làm tác vụ.

Lời giới thiệu, đọc nguyên văn:

> "Mình đang làm khóa luận về một trang web bán thực phẩm có trợ lý AI. Hôm nay
> mình muốn xem trang web có dễ dùng không, chứ không kiểm tra bạn. Nếu bạn thấy
> khó hay làm không được, đó là lỗi của trang web và là thứ mình cần biết. Mình sẽ
> hỏi vài câu về thói quen mua thực phẩm, rồi nhờ bạn làm ba việc trên trang, cuối
> cùng điền một phiếu 10 câu. Khoảng 20 - 25 phút. Mình chỉ ghi chép, không quay phim,
> không ghi âm, tên bạn không xuất hiện trong báo cáo. Bạn dừng lúc nào cũng được.
> Bạn đồng ý tham gia không?"

## 5. Phỏng vấn nhu cầu

Ghi câu trả lời gần nguyên văn, không gợi ý đáp án. Câu 2 cho một mốc thời gian
thực tế để so với KPI 5 phút; câu 4, 5 cho biết người mua có cần trợ lý AI không.

1. Bạn thường mua thực phẩm ở đâu? Có mua qua mạng không, qua app hay trang nào,
   bao lâu một lần?
2. Lần gần nhất mua thực phẩm qua mạng, bạn mua gì? Từ lúc mở app tới lúc đặt xong
   mất khoảng bao lâu?
3. Khi mua thực phẩm qua mạng, chỗ nào làm bạn mất thời gian hoặc khó chịu nhất?
4. Bạn đã dùng chatbot hay trợ lý ảo khi mua sắm chưa? Nếu có, nó giúp được gì,
   chỗ nào chưa được?
5. Nếu chỉ cần gõ "lấy 2 hộp sữa" là hàng vào giỏ, bạn có muốn dùng không? Vì sao?
6. Mua thực phẩm qua mạng bạn thường trả tiền thế nào?

## 6. Tác vụ

Đọc từng tác vụ cho người thử, đưa kèm tờ giấy in đúng câu đó. Bấm giờ từ lúc đọc
xong tới lúc người thử nói "xong" hoặc màn hình đạt điều kiện thành công.

**Quy tắc cho người điều phối:**

- Không chỉ chỗ bấm. Người thử hỏi thì đáp: "Bạn cứ làm theo cách bạn nghĩ là
  đúng." Im lặng lâu thì nhắc: "Bạn đang nghĩ gì?"
- Tác vụ **thất bại** khi hết thời gian tối đa, người thử bỏ cuộc, hoặc phải chỉ
  cách làm. Đã chỉ thì ghi chỉ gì và để người thử làm tiếp cho xong buổi, nhưng tác
  vụ vẫn tính thất bại và thời gian không vào trung vị.
- Trợ lý lỗi do hệ thống (báo hết lượt, quá tải) cũng tính thất bại, ghi rõ nguyên
  nhân.

### Tác vụ 1: Tìm sản phẩm (không dùng trợ lý)

> "Tối nay bạn định nấu canh rau. Hãy tìm xem cửa hàng có loại rau nào, giá bao
> nhiêu và một gói nặng bao nhiêu. Lần này bạn chưa dùng trợ lý AI nhé."

- **Thành công:** nói đúng tên rau, giá và khối lượng đang hiện trên trang (ngày
  22/11/2026: rau mồng tơi, 5.000 đ, 400 g). **Tối đa:** 3 phút.
- **Ghi:** người thử đi bằng đường nào (ô tìm kiếm, danh mục, cuộn trang chủ).

### Tác vụ 2: Mua hàng nhờ trợ lý AI (tác vụ đo KPI)

> "Bạn cần mua 2 phần đùi bò và 1 trái dưa hấu. Hãy nhờ trợ lý AI (biểu tượng chat ở
> góc màn hình) cho hàng vào giỏ, rồi đặt hàng, trả tiền khi nhận hàng, giao tới
> địa chỉ trên tờ giấy này."

- **Bấm giờ:** từ lúc đọc xong câu trên, màn hình ở trang chủ, tới lúc trang đặt
  hàng thành công hiện ra. **Tối đa:** 10 phút.
- **Thành công:** đơn có đúng 2 đùi bò và 1 dưa hấu, trả tiền khi nhận hàng. Người
  thử cho hàng vào giỏ bằng nút thường, không qua trợ lý, thì vẫn tính đặt xong đơn
  nhưng ghi "không dùng trợ lý" và nêu riêng trong báo cáo. Sai sản phẩm hoặc sai
  số lượng là thất bại.
- **Ghi:** từng câu người thử gõ cho trợ lý và trợ lý trả lời gì; có nút xác nhận
  không, đúng hay sai; người thử bấm nút thanh toán trong chat hay tự vào giỏ hàng;
  chỗ dừng lâu hơn 15 giây; mã đơn, để đối chiếu và dọn sau buổi.

### Tác vụ 3: Xem lại đơn vừa đặt

> "Hãy tìm lại đơn bạn vừa đặt và cho mình biết đơn đang ở trạng thái nào."

- **Thành công:** mở được đơn trong trang tài khoản và đọc đúng trạng thái "Đang
  xử lý". **Tối đa:** 3 phút.
- Tác vụ 2 không ra được đơn thì bỏ tác vụ 3, tính là không thực hiện, không đưa
  vào mẫu số.

## 7. Phiếu SUS

Thang SUS gốc của Brooke (1996), dịch sang tiếng Việt, giữ thứ tự câu khen và câu
chê xen kẽ. Người thử chấm ngay sau tác vụ cuối, mỗi câu từ 1 (Hoàn toàn không
đồng ý) tới 5 (Hoàn toàn đồng ý).

1. Tôi nghĩ tôi sẽ muốn dùng trang web này thường xuyên.
2. Tôi thấy trang web này phức tạp một cách không cần thiết.
3. Tôi thấy trang web này dễ dùng.
4. Tôi nghĩ tôi cần người rành kỹ thuật giúp mới dùng được trang web này.
5. Tôi thấy các chức năng của trang web được kết nối với nhau hợp lý.
6. Tôi thấy trang web có quá nhiều chỗ không nhất quán.
7. Tôi nghĩ phần lớn mọi người sẽ học cách dùng trang web này rất nhanh.
8. Tôi thấy trang web này rất rườm rà, khó dùng.
9. Tôi thấy tự tin khi dùng trang web này.
10. Tôi phải học nhiều thứ trước khi dùng được trang web này.

**Cách tính.** Câu lẻ lấy điểm chấm trừ 1, câu chẵn lấy 5 trừ điểm chấm; cộng mười
số rồi nhân 2,5, được điểm từ 0 tới 100. Bỏ trống một câu thì hỏi lại ngay tại
buổi; vẫn trống thì phiếu đó không tính điểm.

## 8. Mẫu biên bản

Mỗi buổi một file `docs/experiment/NTx.md`, chép mẫu dưới đây và điền theo ghi
chép trên giấy. Phần phỏng vấn và phần tác vụ ghi tách nhau.

```markdown
# Biên bản thực nghiệm NTx

- Ngày, giờ: dd/mm/2026, hh:mm - hh:mm
- Nơi: ...
- Người thử: NTx, <nhóm tuổi>, <nghề nghiệp chung>; mua thực phẩm online <tần suất>
- Thiết bị: laptop của sinh viên, Chrome, tài khoản ntx
- Trước buổi: health ok; câu thử trợ lý trả lời trong ... giây
- Đồng ý tham gia: có

## Phần 1. Phỏng vấn nhu cầu
1. ...
2. ... (thời gian lần mua gần nhất: ... phút)
3. ...
4. ...
5. ...
6. ...

## Phần 2. Tác vụ
| Tác vụ | Kết quả | Thời gian | Có phải chỉ không | Ghi chú |
|---|---|---|---|---|
| 1. Tìm rau | Thành công / Thất bại | m:ss | Không / Có: ... | đi bằng ... |
| 2. Mua bằng trợ lý | Thành công / Thất bại | m:ss | ... | mã đơn ...; dùng trợ lý: có / không |
| 3. Xem đơn | Thành công / Thất bại / Không thực hiện | m:ss | ... | ... |

Hội thoại với trợ lý ở tác vụ 2:
- Người thử: "..." -> Trợ lý: "..." (nút: <sản phẩm> x <số lượng>, đúng / sai)

Chỗ người thử dừng lâu hoặc lúng túng:
- ...

## Phần 3. SUS
| Câu | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Điểm chấm | | | | | | | | | | |
Điểm SUS: ...

## Lỗi phát hiện
- <mô tả> -> ghi vào ISSUES.md mã L-..., hoặc "không phải lỗi, ghi vào hạn chế"
```

## 9. Sau mỗi buổi

1. Điền biên bản ngay trong ngày.
2. Đối chiếu mã đơn với biên bản: đúng sản phẩm, số lượng, phương thức trả tiền.
3. Nhân viên chuyển đơn thử sang Đã hủy. Đơn hủy từ Đang xử lý không đụng tồn kho
   (D-032, D-033) và không vào doanh thu (`revenue_orders()`), nhưng số đơn và danh
   sách đơn mới trên trang thống kê vẫn có các đơn này.
4. Lỗi của hệ thống ghi vào `ISSUES.md` kèm mã người thử, sửa ở Tuần 12; chỗ khó
   dùng mà không phải lỗi thì ghi vào phần hạn chế của báo cáo.

## 10. Tổng hợp

Sau buổi cuối, lập `docs/experiment/README.md`: mỗi người thử một dòng (kết quả ba
tác vụ, thời gian tác vụ 2, điểm SUS), dòng cuối là các chỉ số ở mục 1 so với
ngưỡng. Từ bảng này viết chương 5 của báo cáo và báo cáo thực nghiệm nộp trên
portal.
