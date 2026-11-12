"""
The test catalog and the sample requests for measuring the AI assistant (P-42 d, D-062).

The script run_eval.py builds this catalog in a throw-away database, sends every
case to /api/v1/chat/ with the real Gemini, and compares what the server proposed
for the cart with the expected answer below.

CATALOG: products keyed by a short name that the cases refer to. A few are there
on purpose:
- two carrots and two fresh milks, so a vague request matches several (AC-17.3);
- nuoc_mam has only 8 in stock, for a request above the stock;
- tao has nothing in stock and bo_sap is hidden from customers ("draft");
- "unit" goes to weight_volume, which Gemini reads with the search results.
  Left out, every product would say "1 kg", the model default.

CASES: each case has
- id: short name used in the report and with --only;
- group: what the case checks (see GROUPS);
- language: the language of the chat page the customer is on;
- messages: what the customer types, one message after another; only the
  server's answer to the LAST message is checked;
- expect, one of:
    ("add", key, qty)   the server asks to confirm `qty` of product `key`;
    ("choose", [keys])  the customer gets to pick among exactly these products,
                        by buttons (choose_product) or because Gemini lists them
                        and asks in words (no cart proposal at all);
    ("none",)           nothing is proposed for the cart.
"""

from decimal import Decimal

CATALOG = {
    "ca_rot": {"title": "Cà rốt Đà Lạt 500g", "price": Decimal("25000"), "stock": 40, "unit": "500 g"},
    "ca_rot_baby": {"title": "Cà rốt baby 300g", "price": Decimal("32000"), "stock": 25, "unit": "300 g"},
    "sua_vinamilk": {"title": "Sữa tươi Vinamilk không đường 1L", "price": Decimal("36000"), "stock": 30, "unit": "1 lít"},
    "sua_th": {"title": "Sữa tươi TH true MILK ít đường 1L", "price": Decimal("38000"), "stock": 30, "unit": "1 lít"},
    "dua_hau": {"title": "Dưa hấu Long An", "price": Decimal("45000"), "stock": 15, "unit": "1 quả, khoảng 2 kg"},
    "dui_bo": {"title": "Đùi bò Úc 150g", "price": Decimal("89000"), "stock": 20, "unit": "150 g"},
    "trung": {"title": "Trứng gà ta hộp 10 quả", "price": Decimal("42000"), "stock": 50, "unit": "hộp 10 quả"},
    "ca_chua": {"title": "Cà chua bi 300g", "price": Decimal("22000"), "stock": 30, "unit": "300 g"},
    "gao": {"title": "Gạo ST25 túi 5kg", "price": Decimal("185000"), "stock": 12, "unit": "túi 5 kg"},
    "nuoc_mam": {"title": "Nước mắm Phú Quốc 500ml", "price": Decimal("65000"), "stock": 8, "unit": "chai 500 ml"},
    "chuoi": {"title": "Chuối già Nam Mỹ 1kg", "price": Decimal("28000"), "stock": 40, "unit": "1 kg"},
    "bap_cai": {"title": "Bắp cải trắng 1kg", "price": Decimal("18000"), "stock": 20, "unit": "1 kg"},
    "tao": {"title": "Táo Envy New Zealand 1kg", "price": Decimal("120000"), "stock": 0, "unit": "1 kg"},
    "bo_sap": {"title": "Bơ sáp Đắk Lắk 1kg", "price": Decimal("55000"), "stock": 20, "status": "draft", "unit": "1 kg"},
}

GROUPS = {
    "A": "Rõ sản phẩm, rõ số lượng",
    "B": "Số lượng viết bằng chữ",
    "C": "Khách viết tiếng Anh",
    "D": "Tên hàng viết chung chung",
    "E": "Số lượng lớn hơn thường lệ",
    "F": "Nhiều sản phẩm cùng khớp",
    "G": "Không được thêm gì vào giỏ",
    "H": "Hai lượt hội thoại",
}

CASES = [
    # A - the product and the quantity are both clear.
    {"id": "A1", "group": "A", "language": "vi",
     "messages": ["Thêm 2 hộp sữa tươi Vinamilk vào giỏ"], "expect": ("add", "sua_vinamilk", 2)},
    {"id": "A2", "group": "A", "language": "vi",
     "messages": ["Cho tôi 1 quả dưa hấu"], "expect": ("add", "dua_hau", 1)},
    {"id": "A3", "group": "A", "language": "vi",
     "messages": ["Mua 3 hộp cà chua bi"], "expect": ("add", "ca_chua", 3)},
    {"id": "A4", "group": "A", "language": "vi",
     "messages": ["Thêm gạo ST25 vào giỏ giúp mình"], "expect": ("add", "gao", 1)},
    {"id": "A5", "group": "A", "language": "vi",
     "messages": ["Lấy 2 chai nước mắm Phú Quốc"], "expect": ("add", "nuoc_mam", 2)},
    {"id": "A6", "group": "A", "language": "vi",
     "messages": ["Bỏ vào giỏ 5 kg chuối"], "expect": ("add", "chuoi", 5)},

    # B - the quantity is written in words.
    {"id": "B1", "group": "B", "language": "vi",
     "messages": ["Cho mình ba hộp trứng gà"], "expect": ("add", "trung", 3)},
    {"id": "B2", "group": "B", "language": "vi",
     "messages": ["Thêm hai cái bắp cải"], "expect": ("add", "bap_cai", 2)},
    {"id": "B3", "group": "B", "language": "vi",
     "messages": ["Lấy một chục hộp trứng gà"], "expect": ("add", "trung", 10)},
    {"id": "B4", "group": "B", "language": "vi",
     "messages": ["Thêm một tá hộp sữa Vinamilk"], "expect": ("add", "sua_vinamilk", 12)},

    # C - the customer writes in English; product titles are in Vietnamese (L-31).
    {"id": "C1", "group": "C", "language": "en",
     "messages": ["Add 2 watermelons to my cart"], "expect": ("add", "dua_hau", 2)},
    {"id": "C2", "group": "C", "language": "en",
     "messages": ["Please add 3 boxes of eggs to my cart"], "expect": ("add", "trung", 3)},
    {"id": "C3", "group": "C", "language": "en",
     "messages": ["Add one bag of ST25 rice"], "expect": ("add", "gao", 1)},

    # D - a general word the title does not hold, like "thịt bò" (L-42, D-049).
    {"id": "D1", "group": "D", "language": "vi",
     "messages": ["Có bán bò không? Lấy 1 phần nhé"], "expect": ("add", "dui_bo", 1)},
    {"id": "D2", "group": "D", "language": "vi",
     "messages": ["Thêm 2 phần thịt bò vào giỏ"], "expect": ("add", "dui_bo", 2)},
    {"id": "D3", "group": "D", "language": "vi",
     "messages": ["Mua 1 kg trái chuối"], "expect": ("add", "chuoi", 1)},

    # E - more than LARGE_QTY = 10: still proposed, with the ask-again sentence (AC-17.2).
    {"id": "E1", "group": "E", "language": "vi",
     "messages": ["Thêm 20 hộp trứng gà"], "expect": ("add", "trung", 20)},
    {"id": "E2", "group": "E", "language": "vi",
     "messages": ["Cho tôi 11 hộp cà chua bi"], "expect": ("add", "ca_chua", 11)},

    # F - several products match, so the customer must pick (AC-17.3).
    {"id": "F1", "group": "F", "language": "vi",
     "messages": ["Thêm 1 gói cà rốt"], "expect": ("choose", ["ca_rot", "ca_rot_baby"])},
    {"id": "F2", "group": "F", "language": "vi",
     "messages": ["Mua 2 hộp sữa tươi"], "expect": ("choose", ["sua_vinamilk", "sua_th"])},
    {"id": "F3", "group": "F", "language": "en",
     "messages": ["Add 1 pack of carrots"], "expect": ("choose", ["ca_rot", "ca_rot_baby"])},

    # G - nothing may go to the cart.
    {"id": "G1", "group": "G", "language": "vi",  # out of stock
     "messages": ["Thêm 1 kg táo Envy"], "expect": ("none",)},
    {"id": "G2", "group": "G", "language": "vi",  # hidden from customers
     "messages": ["Cho tôi 1 kg bơ sáp"], "expect": ("none",)},
    {"id": "G3", "group": "G", "language": "vi",  # not sold here
     "messages": ["Thêm 2 quả sầu riêng"], "expect": ("none",)},
    {"id": "G4", "group": "G", "language": "vi",  # only 8 in stock
     "messages": ["Lấy 10 chai nước mắm Phú Quốc"], "expect": ("none",)},
    {"id": "G5", "group": "G", "language": "vi",  # a question, not an order
     "messages": ["Dưa hấu giá bao nhiêu vậy?"], "expect": ("none",)},
    {"id": "G6", "group": "G", "language": "vi",  # a question, not an order
     "messages": ["Shop có những loại sữa tươi nào?"], "expect": ("none",)},

    # H - the order is made in the second message, from what the first one found (AC-17.4, L-38).
    {"id": "H1", "group": "H", "language": "vi",
     "messages": ["Tìm giúp mình cà rốt", "Lấy 2 gói cà rốt baby"], "expect": ("add", "ca_rot_baby", 2)},
    {"id": "H2", "group": "H", "language": "vi",
     "messages": ["Thêm 1 quả dưa hấu", "À không, cho mình 3 quả"], "expect": ("add", "dua_hau", 3)},
    {"id": "H3", "group": "H", "language": "vi",
     "messages": ["Có sữa tươi không?", "Lấy 1 hộp TH true MILK"], "expect": ("add", "sua_th", 1)},
]
