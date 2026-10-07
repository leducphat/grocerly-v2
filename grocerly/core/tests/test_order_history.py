"""
Order history tests (UC-13, CN-14): what a customer reads about their own orders.

SRS.md §6.1: the status of an order is shown in the language of the page, not as
the value stored in the database. "Shipped" used to appear as it is on the
Vietnamese site, and it reads like "already delivered" (D-033).
"""

import pytest
from django.urls import reverse
from django.utils import translation

pytestmark = pytest.mark.django_db


def test_order_status_is_shown_in_vietnamese_by_default(customer_client, shipped_order):
    shipped_order()

    response = customer_client.get(reverse("core:dashboard"))

    page = response.content.decode()
    assert "<td>Đang giao hàng</td>" in page
    assert "Shipped" not in page


def test_order_status_is_shown_in_english_on_the_english_site(customer_client, shipped_order):
    shipped_order()

    # A request to /en/ switches the whole test thread to English and nothing
    # switches it back, so the tests running after this one would get English
    # pages too. override() restores the language when the block ends.
    with translation.override("en"):
        response = customer_client.get(reverse("core:dashboard"))

    assert "<td>Shipping</td>" in response.content.decode()


def test_cancelled_order_is_labelled_cancelled_for_the_customer(customer_client, shipped_order):
    shipped_order(status="cancelled")

    response = customer_client.get(reverse("core:dashboard"))

    assert "<td>Đã hủy</td>" in response.content.decode()
