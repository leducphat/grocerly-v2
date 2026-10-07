"""
Order management tests (UC-20, CN-22): who may change the status of an order,
which values the server accepts, and what a status change does to the stock.

The rules under test are the ones SRS.md §6.1 states for UC-20: an order only
moves forward, one step at a time (processing, shipped, delivered), and an order
already `delivered` cannot change status any more (L-5 and L-11 in
docs/COMMITMENT.md). The staff may also cancel an order that is not delivered
yet; `cancelled` is final too (D-033).
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
    order_with_item.product_status = "shipped"
    order_with_item.save()

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


def test_customer_cannot_change_the_status_of_an_order(
    customer_client, order_with_item, product
):
    # `shipped` is the one step the staff may take from here, so only the missing
    # permission can be what stops this request.
    change_status(customer_client, order_with_item, "shipped")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "processing"
    assert product.stock_count == 10


def test_shipped_order_cannot_be_moved_back_to_processing(
    staff_client, order_with_item, product
):
    """L-11: an order only moves forward. A step back would let it enter `shipped`
    a second time, and every entry deducts the stock."""
    change_status(staff_client, order_with_item, "shipped")

    change_status(staff_client, order_with_item, "processing")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "shipped"
    assert product.stock_count == 7  # 10 in stock, 3 ordered, deducted once


def test_sending_the_status_an_order_already_has_changes_nothing(
    staff_client, order_with_item, product
):
    """L-11: a second click on Save must not run the shipping step again. The stock
    is deducted once, when the order first becomes `shipped`."""
    change_status(staff_client, order_with_item, "shipped")

    change_status(staff_client, order_with_item, "shipped")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "shipped"
    assert product.stock_count == 7  # 10 in stock, 3 ordered, deducted once


def test_processing_order_cannot_skip_straight_to_delivered(
    staff_client, order_with_item, product
):
    """Skipping `shipped` would hand over the goods without ever deducting the stock."""
    change_status(staff_client, order_with_item, "delivered")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "processing"
    assert product.stock_count == 10  # nothing left the store
    assert order_with_item.paid_status is False  # so no cash was collected either


# ---------- Cancelling an order (D-033) ----------


def test_processing_order_can_be_cancelled(staff_client, order_with_item, product):
    change_status(staff_client, order_with_item, "cancelled")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "cancelled"
    assert product.stock_count == 10  # nothing had left the store yet
    assert order_with_item.paid_status is False  # no cash is collected for it


def test_cancelling_shipped_order_does_not_put_the_stock_back(
    staff_client, order_with_item, product
):
    """Fresh food that went out with the courier may not be sellable any more, so
    the staff corrects the stock by hand on the product page."""
    change_status(staff_client, order_with_item, "shipped")

    change_status(staff_client, order_with_item, "cancelled")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "cancelled"
    assert product.stock_count == 7  # still the 10 - 3 of the shipping step


def test_delivered_order_cannot_be_cancelled(staff_client, order_with_item):
    order_with_item.product_status = "delivered"
    order_with_item.save()

    change_status(staff_client, order_with_item, "cancelled")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "delivered"


def test_cancelled_order_cannot_be_reopened(staff_client, order_with_item):
    order_with_item.product_status = "cancelled"
    order_with_item.save()

    change_status(staff_client, order_with_item, "processing")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "cancelled"


def test_cancelled_order_cannot_be_shipped(staff_client, order_with_item, product):
    """`cancelled` is final. Shipping it anyway would deduct the stock for goods
    that never leave the store."""
    order_with_item.product_status = "cancelled"
    order_with_item.save()

    change_status(staff_client, order_with_item, "shipped")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "cancelled"
    assert product.stock_count == 10


def test_cancelled_order_cannot_be_marked_delivered(staff_client, order_with_item):
    """Marking a COD order delivered also marks it paid - not for a cancelled one."""
    order_with_item.product_status = "cancelled"
    order_with_item.save()

    change_status(staff_client, order_with_item, "delivered")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "cancelled"
    assert order_with_item.paid_status is False


def test_cancelling_order_paid_through_vnpay_keeps_it_paid(
    staff_client, order_with_item
):
    """The store holds the money until it is refunded outside the system, so the
    order must not read as unpaid."""
    order_with_item.payment_method = "online"
    order_with_item.paid_status = True
    order_with_item.save()

    change_status(staff_client, order_with_item, "cancelled")

    order_with_item.refresh_from_db()
    assert order_with_item.product_status == "cancelled"
    assert order_with_item.paid_status is True


# ---------- Status labels on the staff pages (D-033) ----------


def test_order_list_shows_the_status_label_not_the_stored_value(
    staff_client, order_with_item
):
    change_status(staff_client, order_with_item, "shipped")

    response = staff_client.get(reverse("useradmin:orders"))

    page = response.content.decode()
    assert "Đang giao hàng" in page  # Vietnamese is the default language
    assert "Shipped" not in page


def test_order_detail_offers_cancelled_in_the_status_list(staff_client, order_with_item):
    response = staff_client.get(
        reverse("useradmin:order_detail", args=[order_with_item.id])
    )

    page = response.content.decode()
    assert '<option value="cancelled">Đã hủy</option>' in page
    assert "Order Status: Đang xử lý" in page
