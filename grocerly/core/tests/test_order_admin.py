"""
Orders in the Django admin (UC-25, CN-28).

SRS.md §6.1: the admin may not delete an order for good, the orders are kept for
the accounts. The staff dashboard has no delete button for orders (CN-22). The
Django admin used to offer the Delete button and the "Delete selected" action on
orders and on order lines (L-40); now both admins refuse every delete.
"""

import pytest
from django.urls import reverse

from core.models import CartOrder, CartOrderItem

pytestmark = pytest.mark.django_db


@pytest.fixture
def order_line(order, product):
    """One line of `order`: 2 units of `product`, as checkout writes it."""
    return CartOrderItem.objects.create(
        order=order,
        invoice_no=f"INVOICE_NO-{order.id}",
        product=product,
        item=product.title,
        quantity=2,
        price=product.price,
        total=product.price * 2,
    )


def try_to_delete(client, model, row, way):
    """Delete `row` from the Django admin of `model` ("cartorder" or "cartorderitem"),
    either with the Delete button of its page or with the bulk action of the list."""
    if way == "delete_button":
        url = reverse(f"admin:core_{model}_delete", args=[row.pk])
        return client.post(url, {"post": "yes"})
    return client.post(
        reverse(f"admin:core_{model}_changelist"),
        {"action": "delete_selected", "_selected_action": [row.pk], "post": "yes"},
    )


@pytest.mark.parametrize("way", ["delete_button", "delete_selected"])
def test_django_admin_cannot_delete_an_order(superuser_client, order, way):
    try_to_delete(superuser_client, "cartorder", order, way)

    assert CartOrder.objects.filter(pk=order.pk).exists()


@pytest.mark.parametrize("way", ["delete_button", "delete_selected"])
def test_django_admin_cannot_delete_an_order_line(superuser_client, order_line, way):
    # L-40: the list of order lines has its own admin page, it must not be a way around.
    try_to_delete(superuser_client, "cartorderitem", order_line, way)

    assert CartOrderItem.objects.filter(pk=order_line.pk).exists()


def test_delete_page_of_an_order_is_forbidden(superuser_client, order):
    response = superuser_client.get(reverse("admin:core_cartorder_delete", args=[order.pk]))

    assert response.status_code == 403


def test_order_admin_pages_still_open_for_the_superuser(superuser_client, order_line):
    # UC-25: the admin still reads every order and every line; only deleting is gone.
    urls = [
        reverse("admin:core_cartorder_changelist"),
        reverse("admin:core_cartorder_change", args=[order_line.order.pk]),
        reverse("admin:core_cartorderitem_changelist"),
        reverse("admin:core_cartorderitem_change", args=[order_line.pk]),
    ]

    statuses = [superuser_client.get(url).status_code for url in urls]

    assert statuses == [200, 200, 200, 200]


def test_order_page_shows_no_delete_button_and_no_delete_box_on_its_lines(superuser_client, order_line):
    url = reverse("admin:core_cartorder_change", args=[order_line.order.pk])

    page = superuser_client.get(url).content.decode()

    assert order_line.item in page  # the line is listed in the inline
    assert reverse("admin:core_cartorder_delete", args=[order_line.order.pk]) not in page
    assert "cartorderitem_set-0-DELETE" not in page  # CartOrderItemInline.can_delete
