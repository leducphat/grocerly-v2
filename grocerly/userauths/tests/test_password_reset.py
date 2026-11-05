"""
Forgot password: reset through an emailed link (CN-03, FR-C-01; L-43, D-050).

Until L-43 the mail was only printed to the server log. Now it goes out through
Brevo when BREVO_API_KEY is set. The tests never reach Brevo: the flow tests use
pytest-django's in-memory outbox (`mailoutbox`), and the Brevo tests replace the
HTTP call with a made-up answer, so they check what Grocerly would send and how
it reacts when Brevo refuses.
"""

import json
import logging
import re
from unittest import mock

import pytest
import requests
from django.test import override_settings
from django.urls import reverse

from grocerly.mail import BREVO_BACKEND, CONSOLE_BACKEND, pick_email_backend

pytestmark = pytest.mark.django_db

BREVO_SETTINGS = {
    "EMAIL_BACKEND": BREVO_BACKEND,
    "ANYMAIL": {"BREVO_API_KEY": "test-brevo-key", "REQUESTS_TIMEOUT": 10},
}


def request_reset(client, email):
    return client.post(reverse("userauths:password_reset"), {"email": email})


def reset_link_path(mail_body):
    """The path of the reset link in the mail, without scheme and host."""
    match = re.search(r"https?://testserver(/\S+/password-reset-confirm/\S+/)", mail_body)
    assert match, mail_body
    return match.group(1)


def brevo_answer(status_code, body):
    """A requests.Response as Brevo would send it, built without the network."""
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode()  # what .json() and .text read
    response.headers["Content-Type"] = "application/json"
    return response


# ---------- choosing the backend ----------


def test_mail_goes_through_brevo_when_api_key_is_set():
    assert pick_email_backend("any-brevo-key") == BREVO_BACKEND


def test_mail_is_printed_to_console_when_api_key_is_missing():
    # A work machine or CI without the key must never send real mail.
    assert pick_email_backend("") == CONSOLE_BACKEND


# ---------- the reset flow ----------


def test_password_reset_mails_link_to_registered_email(client, customer, mailoutbox):
    response = request_reset(client, customer.email)

    assert response.status_code == 302
    assert response.url == reverse("userauths:password_reset_done")
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.to == [customer.email]
    assert mail.from_email == "Grocerly <shop@example.com>"  # DEFAULT_FROM_EMAIL
    assert "/password-reset-confirm/" in mail.body


def test_password_reset_for_unknown_email_sends_nothing_but_shows_same_page(client, mailoutbox):
    # Same answer as for a real account, so the page does not tell which emails exist.
    response = request_reset(client, "khongco@example.com")

    assert response.status_code == 302
    assert response.url == reverse("userauths:password_reset_done")
    assert mailoutbox == []


def test_link_in_reset_mail_sets_new_password(client, customer, mailoutbox):
    request_reset(client, customer.email)
    link = reset_link_path(mailoutbox[0].body)

    # The link redirects once to a set-password URL that hides the token.
    form_page = client.get(link, follow=True)
    assert form_page.status_code == 200
    set_password_url = form_page.redirect_chain[-1][0]
    new_password = "Mat-khau-moi#2026"
    response = client.post(
        set_password_url, {"new_password1": new_password, "new_password2": new_password}
    )

    assert response.status_code == 302
    assert response.url == reverse("userauths:password_reset_complete")
    customer.refresh_from_db()
    assert customer.check_password(new_password)


def test_reset_link_cannot_be_used_twice(client, customer, mailoutbox):
    request_reset(client, customer.email)
    link = reset_link_path(mailoutbox[0].body)
    set_password_url = client.get(link, follow=True).redirect_chain[-1][0]
    new_password = "Mat-khau-moi#2026"
    client.post(set_password_url, {"new_password1": new_password, "new_password2": new_password})

    second_try = client.get(link, follow=True)

    # The token is tied to the old password, so the page says the link is invalid
    # and shows no form.
    assert second_try.status_code == 200
    assert second_try.context["validlink"] is False


# ---------- sending through Brevo ----------


@override_settings(**BREVO_SETTINGS)
def test_reset_mail_is_posted_to_brevo_api(client, customer):
    answer = brevo_answer(201, {"messageId": "<test-id@smtp-relay.brevo.com>"})
    with mock.patch.object(requests.Session, "request", return_value=answer) as call:
        response = request_reset(client, customer.email)

    assert response.status_code == 302
    call.assert_called_once()
    sent = call.call_args.kwargs
    assert sent["method"] == "POST"
    assert sent["url"] == "https://api.brevo.com/v3/smtp/email"
    assert sent["headers"]["api-key"] == "test-brevo-key"
    assert sent["timeout"] == 10
    payload = json.loads(sent["data"])
    assert payload["to"] == [{"email": customer.email}]
    assert payload["sender"] == {"email": "shop@example.com", "name": "Grocerly"}
    assert "/password-reset-confirm/" in payload["textContent"]


@override_settings(**BREVO_SETTINGS)
def test_brevo_refusing_mail_is_logged_and_page_still_answers(client, customer, caplog):
    # For example an expired key: Brevo answers 401. The customer still sees the
    # "check your inbox" page; the error goes to the server log (Render Logs).
    answer = brevo_answer(401, {"code": "unauthorized", "message": "Key not found"})
    with mock.patch.object(requests.Session, "request", return_value=answer):
        with caplog.at_level(logging.ERROR, logger="django.contrib.auth"):
            response = request_reset(client, customer.email)

    assert response.status_code == 302
    assert response.url == reverse("userauths:password_reset_done")
    assert f"Failed to send password reset email to {customer.pk}" in caplog.text
    assert "test-brevo-key" not in caplog.text


@override_settings(**BREVO_SETTINGS)
def test_brevo_not_answering_is_logged_and_page_still_answers(client, customer, caplog):
    # Brevo down or slower than REQUESTS_TIMEOUT: same outcome as a refusal.
    with mock.patch.object(requests.Session, "request", side_effect=requests.Timeout("too slow")):
        with caplog.at_level(logging.ERROR, logger="django.contrib.auth"):
            response = request_reset(client, customer.email)

    assert response.status_code == 302
    assert f"Failed to send password reset email to {customer.pk}" in caplog.text


# ---------- how the set-password page shows an error (L-46) ----------


def test_set_password_error_is_shown_in_red_under_its_box(client, customer, mailoutbox, error_under_box):
    request_reset(client, customer.email)
    set_password_url = client.get(reset_link_path(mailoutbox[0].body), follow=True).redirect_chain[-1][0]

    response = client.post(
        set_password_url, {"new_password1": "Mat-khau-moi#2026", "new_password2": "Mat-khau-khac#2026"}
    )

    message = response.context["form"].errors["new_password2"][0]
    assert error_under_box(response.content.decode(), "new_password2", message)
