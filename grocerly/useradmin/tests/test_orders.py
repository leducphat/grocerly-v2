"""
Order management tests (UC-20, CN-22): who may change the status of an order,
which values the server accepts, and what a status change does to the stock.

The rules under test are the ones SRS.md §6.1 states for UC-20: an order only
moves forward, one step at a time (processing, shipped, delivered), and an order
already `delivered` cannot change status any more (L-5 and L-11 in
docs/ISSUES.md). The staff may also cancel an order that is not delivered
yet; `cancelled` is final too (D-033).
"""

import pytest
from django.test import Client
from django.urls import reverse

from core.models import CartOrderItem, Product

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
        reverse("useradmin:order_detail", args=[order_with_item.oid])
    )

    page = response.content.decode()
    assert '<option value="cancelled">Đã hủy</option>' in page
    assert "Order Status: Đang xử lý" in page


def test_shipping_order_deducts_stock_of_product_renamed_after_the_order(
    staff_client, order_with_item, product
):
    product.title = "Cà rốt Đà Lạt loại 1"
    product.save()

    change_status(staff_client, order_with_item, "shipped")

    product.refresh_from_db()
    assert product.stock_count == 7  # 10 in stock, 3 ordered


def test_shipping_order_deducts_stock_of_the_product_bought_not_of_its_namesake(
    staff_client, order_with_item, product
):
    bought = Product.objects.create(title=product.title, price=product.price, stock_count=5)
    CartOrderItem.objects.update(product=bought)

    change_status(staff_client, order_with_item, "shipped")

    bought.refresh_from_db()
    product.refresh_from_db()
    assert (bought.stock_count, product.stock_count) == (2, 10)


def test_shipping_order_deducts_stock_of_a_product_deleted_after_the_order(
    staff_client, order_with_item, product
):
    # The goods leave the shelf whether or not the product is still on sale (D-041).
    product.delete()

    change_status(staff_client, order_with_item, "shipped")

    product.refresh_from_db()
    assert product.stock_count == 7


def test_order_line_without_a_product_ships_and_touches_no_stock(
    staff_client, order_with_item, product
):
    CartOrderItem.objects.update(product=None)

    change_status(staff_client, order_with_item, "shipped")

    order_with_item.refresh_from_db()
    product.refresh_from_db()
    assert order_with_item.product_status == "shipped"
    assert product.stock_count == 10  # the title is not used to guess the product


def test_order_status_form_without_csrf_token_is_rejected(staff, order_with_item):
    client = Client(enforce_csrf_checks=True)  # the test client skips CSRF checks by default
    client.force_login(staff)

    response = change_status(client, order_with_item, "shipped")

    order_with_item.refresh_from_db()
    assert response.status_code == 403
    assert order_with_item.product_status == "processing"


def test_stock_update_without_csrf_token_is_rejected(staff, product):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)

    response = client.post(
        reverse("useradmin:update_stock"), {"pid": product.p_id, "stock_count": 0}
    )

    product.refresh_from_db()
    assert response.status_code == 403
    assert product.stock_count == 10


@pytest.mark.parametrize("method", ["get", "post"])
def test_status_change_of_unknown_order_answers_404(staff_client, method):
    # L-39. Like L-32 on the customer side: a mistyped or old link is "not found", not a crash.
    url = reverse("useradmin:change_order_status", args=["khongcodon"])

    response = getattr(staff_client, method)(url, {"status": "shipped"})

    assert response.status_code == 404


# ---------- the staff order page names the order by oid (L-44) ----------
# CLAUDE.md §7: URLs use the ShortUUID, not the primary key. The customer's order
# page moved to oid with L-32 (D-047); the staff page still took the number.


def test_order_detail_is_opened_by_oid(staff_client, order_with_item):
    response = staff_client.get(reverse("useradmin:order_detail", args=[order_with_item.oid]))

    assert response.status_code == 200
    assert response.context["order"] == order_with_item


@pytest.mark.parametrize("unknown", ["khongcodon", "999999"])
def test_order_detail_of_unknown_order_answers_404(staff_client, unknown):
    # A word made .get(id=...) raise ValueError, a number DoesNotExist; both were 500.
    response = staff_client.get(reverse("useradmin:order_detail", args=[unknown]))

    assert response.status_code == 404


@pytest.mark.parametrize("page_name", ["useradmin:orders", "useradmin:dashboard"])
def test_order_lists_link_to_each_order_by_oid(staff_client, order_with_item, page_name):
    page = staff_client.get(reverse(page_name)).content.decode()

    assert reverse("useradmin:order_detail", args=[order_with_item.oid]) in page


def test_rejected_status_change_goes_back_to_the_order_by_oid(staff_client, order_with_item):
    url = reverse("useradmin:change_order_status", args=[order_with_item.oid])

    response = staff_client.post(url, {"status": ""})  # nothing chosen

    assert response.url == reverse("useradmin:order_detail", args=[order_with_item.oid])
