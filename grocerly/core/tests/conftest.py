"""Fixtures for the tests of the core app (cart, checkout, payment)."""

from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import CartOrder


@pytest.fixture
def add_to_cart():
    """Return a function that adds a product to the session cart the way the product
    page does: GET /add-to-cart/ with the product's id and a quantity.

    Passing price= adds a price parameter to the request, the way a customer
    editing the URL would, so a test can check that the server ignores it (L-6).
    """

    def add(client, product, qty=1, price=None):
        data = {"id": product.id, "qty": qty}
        if price is not None:
            data["price"] = price
        return client.get(reverse("core:add-to-cart"), data)

    return add


@pytest.fixture
def order(customer):
    """An unpaid online order of `customer` worth 50,000 VND, as checkout leaves it."""
    return CartOrder.objects.create(
        user=customer,
        price=Decimal("50000.00"),
        full_name="Nguyễn Văn A",
        email=customer.email,
        address="1 Võ Văn Ngân, Thủ Đức",
    )
