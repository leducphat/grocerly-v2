"""
Contact form tests (UC-08, CN-10): the message is stored once, by POST (L-23).
"""

import pytest
from django.test import Client
from django.urls import reverse

from userauths.models import ContactUs

pytestmark = pytest.mark.django_db

MESSAGE = {
    "full_name": "Nguyễn Văn A",
    "email": "khach@example.com",
    "phone": "0900000000",
    "subject": "Hỏi về đơn hàng",
    "message": "Đơn của tôi tới khi nào?",
}


def test_contact_form_stores_the_message(client):
    response = client.post(reverse("core:ajax-contact-form"), MESSAGE)

    assert response.json()["data"]["bool"] is True
    assert ContactUs.objects.get().subject == MESSAGE["subject"]


def test_contact_form_does_not_accept_get_request(client):
    response = client.get(reverse("core:ajax-contact-form"), MESSAGE)

    assert response.status_code == 405
    assert not ContactUs.objects.exists()


def test_contact_form_without_csrf_token_is_rejected():
    client = Client(enforce_csrf_checks=True)

    response = client.post(reverse("core:ajax-contact-form"), MESSAGE)

    assert response.status_code == 403
    assert not ContactUs.objects.exists()
