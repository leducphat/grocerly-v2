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


def ask(client, message):
    return client.post(
        reverse("store_api:api-chat"), {"message": message, "history": []}, content_type="application/json"
    )


# ---------- search_products tool (UC-16) ----------


def test_search_tool_returns_only_products_in_stock(product):
    Product.objects.create(title="Cà rốt baby", price=Decimal("40000.00"), in_stock=False, stock_count=0)

    results = views.search_products("cà rốt")

    assert [r["title"] for r in results] == [product.title]


def test_search_tool_needs_every_word_of_the_query(product):
    results = views.search_products("cà chua")  # "cà" matches "Cà rốt", "chua" does not

    assert results == [{"message": "No matching products found."}]


def test_search_tool_returns_at_most_five_products(db):
    for i in range(6):
        Product.objects.create(title=f"Táo Fuji {i}", price=Decimal("50000.00"), stock_count=5)

    assert len(views.search_products("táo")) == 5


@pytest.mark.xfail(reason="L-10: the AI search filters on `status`, not on `product_status` like the store")
def test_search_tool_does_not_return_product_hidden_from_store(product):
    product.product_status = "disabled"  # hidden from every store page (FR-A-02)
    product.save()

    results = views.search_products("cà rốt")

    assert results == [{"message": "No matching products found."}]


# ---------- chat endpoint (UC-15, UC-17, UC-18) ----------


def test_chat_without_gemini_key_explains_it_is_not_configured(client):
    response = ask(client, "Xin chào")

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


@pytest.mark.xfail(reason="L-9: request_add_to_cart does not check stock (SRS 6.1, UC-17)")
def test_ai_add_to_cart_refuses_out_of_stock_product(client, product, gemini_chat):
    product.in_stock = False
    product.stock_count = 0
    product.save()
    gemini_chat.send_message.side_effect = [
        gemini_reply(tool="request_add_to_cart", product_url_id=product.p_id, qty=1),
        gemini_reply("Sản phẩm này đã hết hàng."),
    ]

    response = ask(client, "Thêm cà rốt vào giỏ")

    assert response.json().get("action") != "confirm_add_cart"
