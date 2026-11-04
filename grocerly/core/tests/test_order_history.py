"""
Order history tests (UC-13, CN-14): what a customer reads about their own orders.

SRS.md §6.1: the status of an order is shown in the language of the page, not as
the value stored in the database. "Shipped" used to appear as it is on the
Vietnamese site, and it reads like "already delivered" (D-033).
"""

import pytest
from django.urls import reverse
from django.utils import translation

from core.models import Address

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


# ---------- Detail of one order (L-32) ----------


@pytest.fixture
def other_customer(django_user_model, password):
    return django_user_model.objects.create_user(
        email="khachkhac@example.com", username="khachkhac", password=password
    )


def test_customer_reads_the_detail_of_their_own_order(customer_client, shipped_order):
    order = shipped_order()

    response = customer_client.get(reverse("core:order-detail", args=[order.oid]))

    assert response.status_code == 200
    assert "Cà rốt Đà Lạt" in response.content.decode()


def test_detail_of_another_customers_order_answers_404(customer_client, shipped_order, other_customer):
    # L-32. The query filters by user, so nothing leaked even before; the page used
    # to crash with a 500 instead of saying "not found".
    order = shipped_order(user=other_customer)

    response = customer_client.get(reverse("core:order-detail", args=[order.oid]))

    assert response.status_code == 404


def test_detail_of_unknown_order_answers_404(customer_client):
    response = customer_client.get(reverse("core:order-detail", args=["nosuchorder"]))

    assert response.status_code == 404


# ---------- Default address (L-33) ----------


def test_get_request_does_not_change_the_default_address(customer_client, customer):
    # L-33. A link on another site sends a GET with the session cookie (SameSite=Lax),
    # the same hole L-19 closed for the cart. The route had no button on any page, so
    # it was removed (D-047); the path is written out because reverse() no longer
    # knows it.
    old_default = Address.objects.create(user=customer, address="1 Võ Văn Ngân", status=True)
    other = Address.objects.create(user=customer, address="2 Lê Văn Việt", status=False)

    response = customer_client.get("/vi/make-default-address/", {"id": other.id})

    assert response.status_code == 404
    old_default.refresh_from_db()
    other.refresh_from_db()
    assert old_default.status is True
    assert other.status is False
