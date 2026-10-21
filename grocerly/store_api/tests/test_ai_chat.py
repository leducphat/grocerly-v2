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


def gemini_reply(text="", tool=None, **tool_args):
    """One Gemini answer: plain text, or a request to call one of our tools."""
    function_call = SimpleNamespace(name=tool, args=tool_args) if tool else None
    return SimpleNamespace(parts=[SimpleNamespace(function_call=function_call)], text=text)


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
        ("vi", "Bạn có muốn thêm **2x Cà rốt Đà Lạt** vào giỏ hàng không?"),
        ("en", "Would you like to add **2x Cà rốt Đà Lạt** to your cart?"),
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
    assert f"href='/{language}/cart/'" in page  # the checkout button keeps the language
