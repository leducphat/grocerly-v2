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


# ---------- The Django admin only reads orders (L-69) ----------
# The staff page moves an order one step at a time, takes the stock once and marks
# a COD order paid on delivery (D-026, D-032, D-033). Editing the same fields in the
# Django admin skipped every one of these rules, so the admin pages of orders and
# order lines are read-only: they still open, but saving changes nothing.


def test_django_admin_cannot_change_an_order(superuser_client, order):
    # A form the old admin accepted: every required box is filled in.
    url = reverse("admin:core_cartorder_change", args=[order.pk])

    superuser_client.post(url, {
        "product_status": "delivered", "paid_status": "on", "price": "1.00", "saved": "0",
        "payment_method": "cod", "full_name": order.full_name, "email": order.email,
        "cartorderitem_set-TOTAL_FORMS": "0", "cartorderitem_set-INITIAL_FORMS": "0",
    })

    order.refresh_from_db()
    assert (order.product_status, order.paid_status, order.price) == ("processing", False, 50000)


def test_django_admin_cannot_change_an_order_line(superuser_client, order_line):
    url = reverse("admin:core_cartorderitem_change", args=[order_line.pk])

    superuser_client.post(url, {
        "order": order_line.order.pk, "invoice_no": order_line.invoice_no, "item": order_line.item,
        "image": "x.jpg", "quantity": "1", "price": "1.00", "total": "1.00", "product_status": "delivered",
    })

    order_line.refresh_from_db()
    assert (order_line.quantity, order_line.total) == (2, order_line.price * 2)


@pytest.mark.parametrize("model", ["cartorder", "cartorderitem"])
def test_django_admin_cannot_add_an_order_by_hand(superuser_client, model):
    response = superuser_client.get(reverse(f"admin:core_{model}_add"))

    assert response.status_code == 403


def test_order_page_in_django_admin_has_no_save_button(superuser_client, order):
    page = superuser_client.get(reverse("admin:core_cartorder_change", args=[order.pk])).content.decode()

    assert order.email in page  # the admin still reads the order (UC-25)
    assert 'name="_save"' not in page
