"""
AI assistant tests (UC-15 to UC-18, CN-16 to CN-19).

Gemini is never called. grocerly/settings_test.py blanks GEMINI_API_KEY, and the
tests that need answers replace the Gemini model with a MagicMock whose replies
are scripted with gemini_reply().
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.urls import reverse
from django.utils import translation

from core.models import Product
from store_api import views

pytestmark = pytest.mark.django_db


class ToolCallReply:
    """A Gemini answer that is only a tool call. Like the real response, it has
    no text: reading .text raises, which is how L-30 reached the customer."""

    def __init__(self, function_call):
        self.parts = [SimpleNamespace(function_call=function_call)]

    @property
    def text(self):
        raise ValueError("The response has no text, only a function call")


def gemini_reply(text="", tool=None, **tool_args):
    """One Gemini answer: plain text, or a request to call one of our tools."""
    if tool:
        return ToolCallReply(SimpleNamespace(name=tool, args=tool_args))
    return SimpleNamespace(parts=[SimpleNamespace(function_call=None)], text=text)


@pytest.fixture
def gemini_chat(monkeypatch):
    """Swap the Gemini model for a mock and return its chat session.
    A test sets chat.send_message.side_effect to the answers Gemini gives, in order."""
    chat = MagicMock()
    model = MagicMock()
    model.start_chat.return_value = chat
    monkeypatch.setattr(views, "model", model)
    monkeypatch.setattr(views, "api_key", "fake-key-for-tests")
    return chat


def ask(client, message, history=None, language=None):
    data = {"message": message, "history": history or []}
    if language:
        data["language"] = language
    return client.post(reverse("store_api:api-chat"), data, content_type="application/json")


# ---------- search_products tool (UC-16) ----------


def test_search_tool_returns_only_products_in_stock(product):
    Product.objects.create(
        title="Cà rốt baby", price=Decimal("40000.00"), stock_count=0, product_status="published"
    )

    results = views.search_products("cà rốt")

    assert [r["title"] for r in results] == [product.title]


def test_search_tool_needs_every_word_of_the_query(product):
    results = views.search_products("cà chua")  # "cà" matches "Cà rốt", "chua" does not

    assert results == [{"message": "No matching products found."}]


def test_search_tool_tells_gemini_to_search_in_vietnamese():
    # L-31: titles are Vietnamese and the search matches words, so "watermelon"
    # found nothing. Gemini reads the docstring as the tool description; whether
    # it then translates can only be checked against the real Gemini.
    assert "Product titles are in Vietnamese" in views.search_products.__doc__


def test_search_tool_finds_nothing_for_an_english_name(product):
    # The search itself does not translate: the query has to arrive in Vietnamese.
    assert views.search_products("carrot") == [{"message": "No matching products found."}]


def test_search_tool_returns_at_most_five_products(db):
    for i in range(6):
        Product.objects.create(
            title=f"Táo Fuji {i}", price=Decimal("50000.00"), stock_count=5, product_status="published"
        )

    assert len(views.search_products("táo")) == 5


def test_search_tool_does_not_return_product_hidden_from_store(product):
    product.product_status = "disabled"  # hidden from every store page (FR-A-02)
    product.save()

    results = views.search_products("cà rốt")

    assert results == [{"message": "No matching products found."}]


def test_search_tool_does_not_return_deleted_product(product):
    product.delete()  # L-28

    assert views.search_products("cà rốt") == [{"message": "No matching products found."}]


def test_bestsellers_tool_does_not_return_deleted_product(product):
    product.featured = True
    product.save()
    product.delete()  # L-28

    assert views.get_bestsellers() == []


def test_bestsellers_tool_does_not_return_product_hidden_from_store(product):
    # L-10: the same visibility question as the store, in every AI tool.
    product.featured = True
    product.product_status = "disabled"
    product.save()

    assert views.get_bestsellers() == []


# ---------- chat endpoint (UC-15, UC-17, UC-18) ----------


def test_chat_without_gemini_key_explains_it_is_not_configured(client):
    response = ask(client, "Hello", language="en")

    assert response.status_code == 200
    assert "Gemini API Key is missing" in response.json()["reply"]


def test_chat_rejects_empty_message(client, gemini_chat):
    response = ask(client, "")

    assert response.status_code == 400


def test_chat_returns_gemini_text_answer(client, gemini_chat):
    gemini_chat.send_message.side_effect = [gemini_reply("Chào bạn, mình giúp gì được?")]

    response = ask(client, "Xin chào")

    assert response.json() == {"reply": "Chào bạn, mình giúp gì được?"}


def test_ai_add_to_cart_asks_user_to_confirm_before_adding(client, product, gemini_chat):
    # UC-17: the assistant proposes, the user confirms in the chat window.
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=2.0)
    ]

    response = ask(client, "Thêm 2 cà rốt vào giỏ")

    body = response.json()
    assert body["action"] == "confirm_add_cart"
    assert (body["product"]["pid"], body["product"]["qty"]) == (product.p_id, 2)
    assert "cart_data_obj" not in client.session  # nothing added yet


def test_ai_add_to_cart_with_unknown_product_tells_gemini_not_found(client, gemini_chat):
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id="khongtontai", qty=1),
        gemini_reply("Xin lỗi, mình không tìm thấy sản phẩm này."),
    ]

    response = ask(client, "Thêm sản phẩm lạ vào giỏ")

    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {"error": "Product not found"}
    assert "action" not in response.json()


def test_ai_search_then_add_to_cart_in_one_turn_asks_user_to_confirm(client, product, gemini_chat):
    # UC-16, UC-17, L-30: "find it and add one" makes Gemini search, then ask for the
    # cart with the p_id it just found. On the host the second answer has no text, so
    # reading response.text raised and the customer got the connection error.
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="search_products", query="cà rốt"),
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=1),
    ]

    response = ask(client, "Tìm cà rốt rồi thêm 1 cái vào giỏ giúp mình")

    body = response.json()
    assert body.get("action") == "confirm_add_cart"
    assert (body["product"]["pid"], body["product"]["qty"]) == (product.p_id, 1)


def test_ai_bestsellers_then_search_then_add_to_cart_in_one_turn_asks_user_to_confirm(
    client, product, gemini_chat
):
    # L-30: the bestseller list carries no p_id, so "add the most popular one" takes
    # three tools in a row, the most one message may use.
    product.featured = True
    product.save()
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="get_bestsellers"),
        gemini_reply(tool="search_products", query=product.title),
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=1),
    ]

    response = ask(client, "Thêm món bán chạy nhất vào giỏ giúp mình")

    assert response.json().get("action") == "confirm_add_cart"
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"]["result"][0]["title"] == product.title


def test_ai_still_calling_tools_after_three_asks_user_to_go_step_by_step(client, product, gemini_chat):
    # L-30: one message may use three tools. If Gemini wants a fourth, there is no
    # text to show; the customer is asked to go step by step, not told the
    # connection failed.
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="search_products", query="cà rốt") for _ in range(4)
    ]

    response = ask(client, "Tìm cà rốt, cà chua, khoai tây rồi thêm hết vào giỏ")

    assert response.status_code == 200
    assert response.json()["reply"] == (
        "Xin lỗi, mình chưa làm xong yêu cầu này trong một lượt. Bạn nói lần lượt từng bước giúp mình nhé?"
    )


def test_ai_search_answer_keeps_results_for_the_next_message(client, product, gemini_chat):
    # UC-16: a plain answer after a search still carries the results, so that the
    # chat window can send them back with the next message ("add the first one").
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="search_products", query="cà rốt"),
        gemini_reply("Shop có Cà rốt Đà Lạt, 25.000 VND."),
    ]

    response = ask(client, "Có cà rốt không?")

    body = response.json()
    assert body["reply"] == "Shop có Cà rốt Đà Lạt, 25.000 VND."
    assert product.p_id in body["hidden_context"]
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"]["result"][0]["title"] == product.title


def test_ai_checkout_request_sends_user_to_checkout(client, gemini_chat):
    # UC-18
    gemini_chat.send_message.side_effect = [gemini_reply(tool="request_checkout")]

    response = ask(client, "Thanh toán giúp mình")

    assert response.json()["action"] == "confirm_checkout"


def test_chat_over_gemini_quota_asks_user_to_retry_later(client, gemini_chat):
    gemini_chat.send_message.side_effect = Exception("429 Quota exceeded. Please retry in 12.5s")

    response = ask(client, "Xin chào")

    assert response.status_code == 200
    assert response.json()["retry_after"] == 12


def test_ai_add_to_cart_refuses_out_of_stock_product(client, product, gemini_chat):
    product.stock_count = 0
    product.save()
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=1),
        gemini_reply("Sản phẩm này đã hết hàng."),
    ]

    response = ask(client, "Thêm cà rốt vào giỏ")

    assert response.json().get("action") != "confirm_add_cart"
    # Gemini is told why, so it can say so instead of inventing an answer.
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {"error": "Product is out of stock"}


def test_ai_add_to_cart_refuses_product_hidden_from_store(client, product, gemini_chat):
    # L-10: a product the shop has hidden does not exist for the assistant either.
    product.product_status = "disabled"
    product.save()
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=1),
        gemini_reply("Xin lỗi, mình không tìm thấy sản phẩm này."),
    ]

    response = ask(client, "Thêm cà rốt vào giỏ")

    assert response.json().get("action") != "confirm_add_cart"
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {"error": "Product not found"}


# ---------- each customer message reaches Gemini once (L-13) ----------


def test_chat_sends_new_message_to_gemini_only_once(client, gemini_chat):
    # L-13: the chat window also put the new message at the end of `history`, so
    # Gemini read "2" twice in a row and proposed 22.
    gemini_chat.send_message.side_effect = [gemini_reply("Mình thêm 2 thùng nhé?")]
    history = [
        {"role": "assistant", "content": "Bạn muốn mua mấy thùng?"},
        {"role": "user", "content": "2"},
    ]

    ask(client, "2", history=history)

    gemini_history = views.model.start_chat.call_args.kwargs["history"]
    assert gemini_history == [{"role": "model", "parts": ["Bạn muốn mua mấy thùng?"]}]
    gemini_chat.send_message.assert_called_once_with("2")


@pytest.mark.parametrize("history", [{"role": "user"}, 5])
def test_chat_with_history_that_is_not_a_list_does_not_crash(client, gemini_chat, history):
    # `history` is written by the browser. Something that is not a list ends in
    # the usual "connection trouble" answer, not in a server error.
    response = ask(client, "2", history=history)

    assert response.status_code == 200
    assert "reply" in response.json()


def test_chat_keeps_an_earlier_turn_with_the_same_words(client, gemini_chat):
    # Only a copy right at the end is dropped: the customer may well have said
    # "2" before, and that turn belongs to the conversation.
    gemini_chat.send_message.side_effect = [gemini_reply("Mình thêm 2 thùng nữa nhé?")]
    history = [
        {"role": "user", "content": "2"},
        {"role": "assistant", "content": "Bạn muốn mua thêm mấy thùng?"},
    ]

    ask(client, "2", history=history)

    gemini_history = views.model.start_chat.call_args.kwargs["history"]
    assert gemini_history == [
        {"role": "user", "parts": ["2"]},
        {"role": "model", "parts": ["Bạn muốn mua thêm mấy thùng?"]},
    ]


# ---------- quantity the assistant may propose (UC-17, L-14) ----------


def test_ai_add_to_cart_refuses_quantity_above_stock(client, product, gemini_chat):
    # L-14: 22 asked, 10 left. The assistant used to propose 22 and the cart took
    # 10; now Gemini is told how many are left so it can say so.
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=22),
        gemini_reply("Kho chỉ còn 10, bạn lấy 10 nhé?"),
    ]

    response = ask(client, "Thêm 22 cà rốt vào giỏ")

    assert response.json().get("action") != "confirm_add_cart"
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {"error": "Only 10 left in stock"}


def test_ai_add_to_cart_proposes_quantity_equal_to_stock(client, product, gemini_chat):
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=10)
    ]

    response = ask(client, "Thêm 10 cà rốt vào giỏ")

    body = response.json()
    assert body["action"] == "confirm_add_cart"
    assert body["product"]["qty"] == 10


def test_ai_add_to_cart_counts_what_the_cart_already_holds(client, product, gemini_chat):
    # L-18: the cart adds to its line, so 3 more on top of 8 is 11, and 10 are left.
    client.post(reverse("core:add-to-cart"), {"id": product.id, "qty": 8})
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=3),
        gemini_reply("Giỏ đã có 8, kho còn 10, bạn lấy thêm 2 nhé?"),
    ]

    response = ask(client, "Thêm 3 cà rốt nữa")

    assert response.json().get("action") != "confirm_add_cart"
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {
        "error": "Only 10 left in stock and the cart already has 8"
    }


def test_ai_add_to_cart_proposes_exactly_what_still_fits(client, product, gemini_chat):
    client.post(reverse("core:add-to-cart"), {"id": product.id, "qty": 8})
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=2)
    ]

    response = ask(client, "Thêm 2 cà rốt nữa")

    body = response.json()
    assert body["action"] == "confirm_add_cart"
    assert body["product"]["qty"] == 2


@pytest.mark.parametrize("qty", [0, -2])
def test_ai_add_to_cart_refuses_quantity_below_one(client, product, gemini_chat, qty):
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=qty),
        gemini_reply("Bạn muốn lấy mấy thùng?"),
    ]

    response = ask(client, "Thêm cà rốt vào giỏ")

    assert response.json().get("action") != "confirm_add_cart"
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {"error": "Quantity must be at least 1"}


# ---------- fixed text of the chat follows the page language (UC-15, L-15) ----------


@pytest.mark.parametrize(
    ("language", "question"),
    [
        ("vi", "Bạn có muốn thêm **2x Cà rốt Đà Lạt** vào giỏ hàng không? "
               "Đơn giá 25.000 ₫, thành tiền **50.000 ₫**."),
        ("en", "Would you like to add **2x Cà rốt Đà Lạt** to your cart? "
               "Unit price 25.000 ₫, total **50.000 ₫**."),
    ],
)
def test_ai_add_to_cart_question_follows_page_language(client, product, gemini_chat, language, question):
    # /api/v1/ is outside i18n_patterns, so the chat window sends the language of
    # the page it sits on.
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=2)
    ]

    response = ask(client, "Thêm 2 cà rốt vào giỏ", language=language)

    assert response.json()["reply"] == question


def test_quota_message_is_in_english_on_the_english_site(client, gemini_chat):
    gemini_chat.send_message.side_effect = Exception("429 Quota exceeded. Please retry in 12.5s")

    response = ask(client, "Hello", language="en")

    assert "Please wait **12 seconds**" in response.json()["reply"]


def test_chat_with_unknown_language_answers_in_vietnamese(client, gemini_chat):
    gemini_chat.send_message.side_effect = [gemini_reply(tool="request_checkout")]

    response = ask(client, "Thanh toán giúp mình", language="fr")

    assert response.json()["reply"].startswith("Bạn có thể xem lại")


def test_chat_with_language_that_is_not_text_answers_in_vietnamese(client, gemini_chat):
    # The request body is the browser's to write; a list here must not crash.
    gemini_chat.send_message.side_effect = [gemini_reply(tool="request_checkout")]

    response = ask(client, "Thanh toán giúp mình", language=["en"])

    assert response.status_code == 200
    assert response.json()["reply"].startswith("Bạn có thể xem lại")


@pytest.mark.parametrize(
    ("language", "button", "user_reply"),
    [
        ("vi", "Có, thêm vào giỏ", "Có, thêm giúp mình nhé."),
        ("en", "Yes, Add to Cart", "Yes, please add it."),
    ],
)
def test_chat_window_text_follows_page_language(client, language, button, user_reply):
    # The same reason as test_order_history.py: a request to /en/ would leave the
    # test thread in English, override() switches it back.
    with translation.override(language):
        page = client.get(reverse("core:index")).content.decode()

    assert f'addButton: "{button}"' in page
    assert f'yesAdd: "{user_reply}"' in page
    assert f'language: "{language}"' in page
    assert f"href = '/{language}/cart/'" in page  # the checkout button keeps the language


# ---------- control over what the assistant proposes (UC-17, SRS §6.2, D-048) ----------


@pytest.fixture
def baby_carrot(product):
    """A second product that a search for "cà rốt" also finds: 40,000 VND, 10 left."""
    return Product.objects.create(
        title="Cà rốt baby", category=product.category, price=Decimal("40000.00"),
        stock_count=10, product_status="published",
    )


def propose(gemini_chat, product, qty, search=None):
    """Script Gemini to search for `search` (if given), then propose `qty` of `product`."""
    replies = [gemini_reply(tool="search_products", query=search)] if search else []
    replies.append(gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=qty))
    gemini_chat.send_message.side_effect = replies


def test_confirm_question_shows_unit_price_and_total(client, product, gemini_chat):
    # AC-17.1: 3 x 25,000 VND, written like the shop pages write prices.
    propose(gemini_chat, product, 3)

    body = ask(client, "Thêm 3 cà rốt vào giỏ").json()

    assert body["reply"].endswith("Đơn giá 25.000 ₫, thành tiền **75.000 ₫**.")
    assert (body["product"]["price"], body["product"]["total"]) == ("25000.00", "75000.00")


def test_confirm_question_uses_the_price_in_the_database(client, product, gemini_chat):
    # AC-17.1: Gemini only names the product; the price is read when it asks.
    Product.objects.filter(pk=product.pk).update(price=Decimal("27500.00"))
    propose(gemini_chat, product, 2)

    body = ask(client, "Thêm 2 cà rốt vào giỏ").json()

    assert "thành tiền **55.000 ₫**" in body["reply"]


def test_search_results_give_gemini_whole_vnd_without_float(product):
    # D-048: money is not written through float.
    assert views.search_products("cà rốt")[0]["price"] == "25000 VND"


def test_more_than_ten_units_makes_the_assistant_ask_again(client, product, gemini_chat):
    # AC-17.2: 11 is the first quantity above the threshold.
    Product.objects.filter(pk=product.pk).update(stock_count=50)
    propose(gemini_chat, product, 11)

    body = ask(client, "Thêm 11 cà rốt vào giỏ").json()

    assert body["action"] == "confirm_add_cart"
    assert body["reply"].startswith("11 là số lượng lớn hơn thường lệ, bạn kiểm tra lại giúp mình nhé.")
    assert body["product"]["large_qty"] is True
    assert body["product"]["label"] == "Đúng 11, thêm vào giỏ"


def test_ten_units_is_asked_as_usual(client, product, gemini_chat):
    # AC-17.2, the boundary: 10 is not above the threshold.
    propose(gemini_chat, product, 10)

    body = ask(client, "Thêm 10 cà rốt vào giỏ").json()

    assert body["reply"].startswith("Bạn có muốn thêm **10x Cà rốt Đà Lạt**")
    assert body["product"]["large_qty"] is False
    assert body["product"]["label"] == "Có, thêm vào giỏ"


def test_large_quantity_above_stock_is_still_refused(client, product, gemini_chat):
    # AC-17.2: the threshold does not replace the stock limit (10 left).
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=30),
        gemini_reply("Kho chỉ còn 10."),
    ]

    response = ask(client, "Thêm 30 cà rốt vào giỏ")

    assert "action" not in response.json()
    second_message = gemini_chat.send_message.call_args_list[1].args[0]
    assert second_message[0]["function_response"]["response"] == {"error": "Only 10 left in stock"}


@pytest.mark.parametrize(
    ("language", "warning", "label"),
    [
        ("vi", "11 là số lượng lớn hơn thường lệ", "Đúng 11, thêm vào giỏ"),
        ("en", "11 is more than usual, please check the quantity.", "Yes, add 11 to cart"),
    ],
)
def test_large_quantity_question_follows_page_language(client, product, gemini_chat, language, warning, label):
    Product.objects.filter(pk=product.pk).update(stock_count=50)
    propose(gemini_chat, product, 11)

    body = ask(client, "Add 11 carrots", language=language).json()

    assert body["reply"].startswith(warning)
    assert body["product"]["label"] == label


def test_two_matches_let_the_customer_choose(client, product, baby_carrot, gemini_chat):
    # AC-17.3: the search found two, Gemini picked one; the customer gets both.
    propose(gemini_chat, baby_carrot, 2, search="cà rốt")

    body = ask(client, "Tìm cà rốt rồi thêm 2 cái vào giỏ").json()

    assert body["action"] == "choose_product"
    assert "product" not in body
    assert [(c["pid"], c["qty"]) for c in body["choices"]] == [(product.p_id, 2), (baby_carrot.p_id, 2)]
    assert [c["label"] for c in body["choices"]] == [
        "Thêm 2x Cà rốt Đà Lạt - 50.000 ₫",
        "Thêm 2x Cà rốt baby - 80.000 ₫",
    ]
    assert "cart_data_obj" not in client.session  # nothing added yet


def test_choices_stay_in_the_history_for_an_answer_in_words(client, product, baby_carrot, gemini_chat):
    # AC-17.3: the customer may type "the second one" instead of clicking.
    propose(gemini_chat, baby_carrot, 1, search="cà rốt")

    body = ask(client, "Thêm cà rốt vào giỏ").json()

    assert baby_carrot.p_id in body["hidden_context"]


def test_choices_leave_out_products_that_cannot_take_the_quantity(client, product, baby_carrot, gemini_chat):
    # AC-17.3: with 1 baby carrot left, only one product can take 2, so there is
    # nothing to choose between.
    Product.objects.filter(pk=baby_carrot.pk).update(stock_count=1)
    propose(gemini_chat, product, 2, search="cà rốt")

    body = ask(client, "Tìm cà rốt rồi thêm 2 cái vào giỏ").json()

    assert body["action"] == "confirm_add_cart"
    assert body["product"]["pid"] == product.p_id


def test_choice_with_a_large_quantity_also_asks_again(client, product, baby_carrot, gemini_chat):
    # AC-17.2 and AC-17.3 together.
    Product.objects.filter(pk__in=[product.pk, baby_carrot.pk]).update(stock_count=50)
    propose(gemini_chat, product, 12, search="cà rốt")

    body = ask(client, "Thêm 12 cà rốt").json()

    assert body["action"] == "choose_product"
    assert body["reply"].startswith("12 là số lượng lớn hơn thường lệ")
    assert all(c["large_qty"] for c in body["choices"])


def test_only_the_latest_search_of_the_message_counts(client, product, baby_carrot, gemini_chat):
    # AC-17.4: Gemini narrowed "cà rốt" (two) down to "cà rốt baby" (one).
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="search_products", query="cà rốt"),
        gemini_reply(tool="search_products", query="cà rốt baby"),
        gemini_reply(tool="request_add_to_cart", product_url_id=baby_carrot.p_id, qty=1),
    ]

    body = ask(client, "Thêm 1 cà rốt baby").json()

    assert body["action"] == "confirm_add_cart"
    assert body["product"]["pid"] == baby_carrot.p_id


def test_a_pick_from_an_earlier_message_is_not_questioned(client, product, baby_carrot, gemini_chat):
    # AC-17.4: the list was shown in the turn before; "the second one" is a choice.
    history = [
        {"role": "user", "content": "Có cà rốt không?"},
        {"role": "assistant", "content": "Có Cà rốt Đà Lạt và Cà rốt baby."},
        {"role": "user", "content": str(views.search_results([product, baby_carrot])), "hidden": True},
    ]
    propose(gemini_chat, baby_carrot, 1)

    body = ask(client, "Thêm cái thứ hai", history=history).json()

    assert body["action"] == "confirm_add_cart"
    assert body["product"]["pid"] == baby_carrot.p_id
