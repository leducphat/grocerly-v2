"""
Order management tests (UC-20, CN-22): who may change the status of an order,
which values the server accepts, and what a status change does to the stock.

The rule under test is the one SRS.md §6.1 states for UC-20: an order already
`delivered` cannot change status any more (L-5 in docs/COMMITMENT.md).
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def change_status(client, order, status):
    """Post the status form of the order detail page, the way the staff does."""
    return client.post(
        reverse("useradmin:change_order_status", args=[order.oid]), {"status": status}
    )


def test_marking_order_shipped_deducts_ordered_quantity_from_stock(
    staff_client, order_with_item, product
):
    change_status(staff_client, order_with_item, "shipped")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "shipped"
    assert product.stock_count == 7  # 10 in stock, 3 ordered


def test_marking_cod_order_delivered_marks_it_paid(staff_client, order_with_item):
    change_status(staff_client, order_with_item, "delivered")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "delivered"
    assert order_with_item.paid_status is True  # the courier collected the cash


def test_delivered_order_cannot_be_moved_back_to_processing(
    staff_client, order_with_item
):
    """L-5: a delivered order is final - the transaction history must stay readable."""
    order_with_item.product_status = "delivered"
    order_with_item.save()

    change_status(staff_client, order_with_item, "processing")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "delivered"


def test_delivered_order_sent_to_shipped_again_does_not_deduct_stock_twice(
    staff_client, order_with_item, product
):
    """L-5: without the guard, every trip through `shipped` subtracts the quantity anew."""
    order_with_item.product_status = "delivered"
    order_with_item.save()

    change_status(staff_client, order_with_item, "shipped")

    product.refresh_from_db()
    assert product.stock_count == 10  # untouched


def test_status_outside_the_three_defined_values_is_rejected(
    staff_client, order_with_item
):
    """"pending" is the placeholder option of the form; submitting it used to be stored."""
    change_status(staff_client, order_with_item, "pending")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "processing"  # as checkout left it


def test_customer_cannot_change_the_status_of_an_order(customer_client, order_with_item):
    change_status(customer_client, order_with_item, "delivered")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "processing"
    assert order_with_item.paid_status is False
