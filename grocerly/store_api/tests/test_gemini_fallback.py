"""
The assistant moves to the next Gemini model when one fails (UC-15, D-060).

Each model in views.GEMINI_MODELS gets its own mock here, so a test can make one
model fail and see which model answered. Gemini itself is never called.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.core.cache import cache
from django.urls import reverse
from google.api_core.exceptions import (
    DeadlineExceeded,
    InvalidArgument,
    NotFound,
    ResourceExhausted,
    ServiceUnavailable,
)

from store_api import views

pytestmark = pytest.mark.django_db

FIRST, SECOND, THIRD, FOURTH = views.GEMINI_MODELS
CONNECTION_TROUBLE = {"reply": "Mình đang gặp trục trặc kết nối. Bạn thử lại sau nhé!"}


def text_reply(text):
    return SimpleNamespace(parts=[SimpleNamespace(function_call=None)], text=text)


def tool_reply(name, **args):
    call = SimpleNamespace(name=name, args=args)
    return SimpleNamespace(parts=[SimpleNamespace(function_call=call)])


@pytest.fixture
def chats(monkeypatch):
    """One mock chat per model, by model name. A test scripts each chat's
    send_message.side_effect; start_chat records the history it was given."""
    chats = {}
    models = {}
    for name in views.GEMINI_MODELS:
        chat = MagicMock(name=f"chat-{name}")
        chat.history = [f"history of {name}"]
        model = MagicMock(name=name)
        model.start_chat.return_value = chat
        chats[name] = chat
        models[name] = model
    monkeypatch.setattr(views, "models", models)
    monkeypatch.setattr(views, "api_key", "fake-key-for-tests")
    return chats


def fake_clock(monkeypatch, *seconds):
    """Make views read these times, in order, instead of the real clock. Only
    views.time is replaced, so Django keeps the real one."""
    readings = iter(seconds)
    monkeypatch.setattr(views, "time", SimpleNamespace(monotonic=lambda: next(readings)))


def ask(client, message="Xin chào"):
    return client.post(
        reverse("store_api:api-chat"),
        {"message": message, "history": []},
        content_type="application/json",
    )


@pytest.mark.parametrize(
    "error",
    [
        ServiceUnavailable("This model is currently experiencing high demand."),
        ResourceExhausted("429 You exceeded your current quota"),
        DeadlineExceeded("Deadline Exceeded"),
    ],
)
def test_chat_answers_from_next_model_when_first_model_fails(client, chats, error):
    chats[FIRST].send_message.side_effect = error
    chats[SECOND].send_message.side_effect = [text_reply("Chào bạn!")]

    response = ask(client)

    assert response.json() == {"reply": "Chào bạn!"}
    chats[THIRD].send_message.assert_not_called()


def test_models_are_tried_in_the_order_of_the_list(client, chats):
    for name in (FIRST, SECOND, THIRD):
        chats[name].send_message.side_effect = ServiceUnavailable("busy")
    chats[FOURTH].send_message.side_effect = [text_reply("Chào bạn!")]

    response = ask(client)

    assert response.json() == {"reply": "Chào bạn!"}
    for name in views.GEMINI_MODELS:
        chats[name].send_message.assert_called_once()


def test_failed_model_is_skipped_by_the_next_message(client, chats):
    chats[FIRST].send_message.side_effect = ServiceUnavailable("busy")
    chats[SECOND].send_message.side_effect = [text_reply("Một"), text_reply("Hai")]
    ask(client)

    ask(client, "Tin nhắn thứ hai")

    # The first model was tried once, by the first message only.
    chats[FIRST].send_message.assert_called_once()
    assert chats[SECOND].send_message.call_count == 2


def test_failed_model_is_tried_again_once_its_skip_time_is_over(client, chats):
    chats[FIRST].send_message.side_effect = [ServiceUnavailable("busy"), text_reply("Đã ổn")]
    chats[SECOND].send_message.side_effect = [text_reply("Dự phòng")]
    ask(client)
    cache.delete(views.skip_key(FIRST))  # what GEMINI_SKIP_SECONDS later looks like

    response = ask(client, "Tin nhắn thứ hai")

    assert response.json() == {"reply": "Đã ổn"}


def test_failed_model_is_remembered_for_five_minutes(client, chats, monkeypatch):
    remembered = {}
    monkeypatch.setattr(views.cache, "set", lambda key, value, timeout: remembered.update({key: timeout}))
    chats[FIRST].send_message.side_effect = ServiceUnavailable("busy")
    chats[SECOND].send_message.side_effect = [text_reply("Chào bạn!")]

    ask(client)

    assert remembered == {views.skip_key(FIRST): 300}


def test_all_models_are_tried_when_every_one_failed_recently(client, chats):
    for name in views.GEMINI_MODELS:
        cache.set(views.skip_key(name), True)
    chats[FIRST].send_message.side_effect = [text_reply("Chào bạn!")]

    response = ask(client)

    assert response.json() == {"reply": "Chào bạn!"}


def test_every_model_failing_answers_connection_trouble(client, chats):
    for name in views.GEMINI_MODELS:
        chats[name].send_message.side_effect = ServiceUnavailable("busy")

    response = ask(client)

    assert response.status_code == 200
    assert response.json() == CONNECTION_TROUBLE


def test_every_model_out_of_quota_asks_customer_to_wait(client, chats):
    for name in views.GEMINI_MODELS:
        chats[name].send_message.side_effect = ResourceExhausted(
            "429 Quota exceeded. Please retry in 12.5s"
        )

    response = ask(client)

    assert response.status_code == 200
    assert response.json()["retry_after"] == 12


@pytest.mark.parametrize(
    "error",
    [NotFound("404 models/gemini-x is not found"), InvalidArgument("400 API key not valid")],
)
def test_configuration_error_is_not_hidden_by_a_fallback(client, chats, error):
    # A wrong model name or key would fail on every model alike; trying the next
    # one only hides the mistake.
    chats[FIRST].send_message.side_effect = error

    response = ask(client)

    assert response.json() == CONNECTION_TROUBLE
    chats[SECOND].send_message.assert_not_called()


def test_model_failing_mid_tool_loop_hands_the_conversation_to_the_next(client, chats):
    # The first model asks for bestsellers, then fails on the tool's answer. The
    # second model must get the conversation so far and the same tool answer.
    chats[FIRST].send_message.side_effect = [
        tool_reply("get_bestsellers"),
        ServiceUnavailable("busy"),
    ]
    chats[SECOND].send_message.side_effect = [text_reply("Món bán chạy là cà rốt.")]

    response = ask(client, "Món nào bán chạy?")

    assert response.json()["reply"] == "Món bán chạy là cà rốt."
    second_model = views.models[SECOND]
    assert second_model.start_chat.call_args.kwargs["history"] == chats[FIRST].history
    resent = chats[SECOND].send_message.call_args.args[0]
    assert resent == chats[FIRST].send_message.call_args.args[0]
    assert resent[0]["function_response"]["name"] == "get_bestsellers"


def test_message_stops_trying_models_after_25_seconds(client, chats, monkeypatch):
    # Clock readings: start, first try, second try (13 s), third try (26 s).
    # By the third try the message is past GEMINI_DEADLINE, so it stops there.
    fake_clock(monkeypatch, 0, 0, 13, 26)
    for name in views.GEMINI_MODELS:
        chats[name].send_message.side_effect = DeadlineExceeded("Deadline Exceeded")

    response = ask(client)

    assert response.json() == CONNECTION_TROUBLE
    chats[FIRST].send_message.assert_called_once()
    chats[SECOND].send_message.assert_called_once()
    chats[THIRD].send_message.assert_not_called()


def test_last_try_gets_only_the_time_left_before_the_deadline(client, chats, monkeypatch):
    # 20 s already spent on the first model: the second gets 5 s, not 8 s.
    fake_clock(monkeypatch, 0, 0, 20)
    chats[FIRST].send_message.side_effect = DeadlineExceeded("Deadline Exceeded")
    chats[SECOND].send_message.side_effect = [text_reply("Chào bạn!")]

    ask(client)

    options = chats[SECOND].send_message.call_args.kwargs["request_options"]
    assert options == {"timeout": 5, "retry": None}
