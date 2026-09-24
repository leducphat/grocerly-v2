"""Fixtures for the tests of the useradmin app (the store staff dashboard)."""

from decimal import Decimal

import pytest

from core.models import CartOrder, CartOrderItem


@pytest.fixture
def staff(db, django_user_model, password):
    """An account of the store staff: it reaches /useradmin/, not the Django admin."""
    return django_user_model.objects.create_user(
        email="nhanvien@example.com",
        username="nhanvien",
        password=password,
        is_staff=True,
    )


@pytest.fixture
def staff_client(client, staff):
    """The Django test client, signed in as `staff`."""
    client.force_login(staff)
    return client


@pytest.fixture
def order_with_item(customer, product):
    """A paid COD order of `customer` holding 3 units of `product`.

    `CartOrderItem` keeps the product's title, not a foreign key - that is how
    checkout writes it, and how change_order_status finds the product again.
    """
    order = CartOrder.objects.create(
        user=customer,
        price=Decimal("75000.00"),
        full_name="Nguyễn Văn A",
        email=customer.email,
        address="1 Võ Văn Ngân, Thủ Đức",
        payment_method="cod",
    )
    CartOrderItem.objects.create(
        order=order,
        invoice_no=f"INVOICE_NO-{order.id}",
        item=product.title,
        quantity=3,
        price=product.price,
        total=product.price * 3,
    )
    return order
