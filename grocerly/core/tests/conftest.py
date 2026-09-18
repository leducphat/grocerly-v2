"""Fixtures for the tests of the core app (cart, checkout, payment)."""

from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import CartOrder


@pytest.fixture
def add_to_cart():
    """Return a function that adds a product to the session cart the way the product
    page does: GET /add-to-cart/ with the product's id, title, quantity and price."""

    def add(client, product, qty=1, price=None):
        return client.get(
            reverse("core:add-to-cart"),
            {
                "id": product.id,
                "pid": product.p_id,
                "title": product.title,
                "image": "products.jpg",
                "qty": qty,
                # The page sends the price it displays. Passing price= lets a test
                # send a different one, like a customer editing the request (L-6).
                "price": product.price if price is None else price,
            },
        )

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
