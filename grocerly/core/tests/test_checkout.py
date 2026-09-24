"""
Checkout tests (UC-09, CN-11): shipping information, coupons, cash on delivery,
and orders of other customers. VNPay is tested in test_payment.py.
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import CartOrder, CartOrderItem, Coupon, Product

pytestmark = pytest.mark.django_db

SHIPPING_INFO = {
    "full_name": "Nguyễn Văn A",
    "email": "khachhang@example.com",
    "mobile": "0901234567",
    "address": "1 Võ Văn Ngân",
    "city": "Thủ Đức",
    "state": "TP.HCM",
    "country": "Việt Nam",
}


def submit_shipping_info(client, data=SHIPPING_INFO):
    return client.post(reverse("core:save_checkout_info"), data)


# ---------- Shipping information → order ----------


def test_checkout_requires_sign_in(client):
    response = client.get(reverse("core:checkout-info"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("userauths:sign-in"))


def test_checkout_without_address_creates_no_order(customer_client, product, add_to_cart):
    add_to_cart(customer_client, product)

    response = submit_shipping_info(customer_client, {**SHIPPING_INFO, "address": ""})

    assert response.url == reverse("core:checkout-info")
    assert CartOrder.objects.count() == 0


def test_checkout_creates_unpaid_order_from_cart(customer_client, customer, product, add_to_cart):
    add_to_cart(customer_client, product, qty=2)

    response = submit_shipping_info(customer_client)

    order = CartOrder.objects.get(user=customer)
    assert response.url == reverse("core:checkout", args=[order.oid])
    assert (order.price, order.paid_status) == (Decimal("50000.00"), False)
    item = CartOrderItem.objects.get(order=order)
    assert (item.item, item.quantity, item.total) == (product.title, 2, Decimal("50000.00"))
    assert customer_client.session["pending_order_oid"] == order.oid


def test_submitting_checkout_twice_keeps_one_order(customer_client, product, add_to_cart):
    add_to_cart(customer_client, product)

    submit_shipping_info(customer_client)
    submit_shipping_info(customer_client)

    assert CartOrder.objects.count() == 1
    assert CartOrderItem.objects.count() == 1


def test_order_total_uses_product_price_not_price_sent_by_browser(
    customer_client, customer, product, add_to_cart
):
    add_to_cart(customer_client, product, qty=2, price="1000")  # real price: 25,000

    submit_shipping_info(customer_client)

    order = CartOrder.objects.get(user=customer)
    assert order.price == product.price * 2


def test_order_quantity_does_not_go_above_stock(customer_client, customer, product, add_to_cart):
    # L-7: the cart is checked again when the order is created, not only when the
    # product is added - the stock may have run down in between.
    add_to_cart(customer_client, product, qty=product.stock_count)
    Product.objects.filter(id=product.id).update(stock_count=3)

    submit_shipping_info(customer_client)

    order = CartOrder.objects.get(user=customer)
    item = CartOrderItem.objects.get(order=order)
    assert (item.quantity, order.price) == (3, product.price * 3)


# ---------- Coupons ----------


def apply_coupon(client, order, code):
    return client.post(reverse("core:checkout", args=[order.oid]), {"code": code})


def test_active_coupon_takes_percentage_off_order(customer_client, order):
    Coupon.objects.create(code="GIAM10", discount=10, active=True)

    apply_coupon(customer_client, order, "GIAM10")

    order.refresh_from_db()
    assert (order.price, order.saved) == (Decimal("45000.00"), Decimal("5000.00"))


def test_same_coupon_is_applied_only_once(customer_client, order):
    Coupon.objects.create(code="GIAM10", discount=10, active=True)

    apply_coupon(customer_client, order, "GIAM10")
    apply_coupon(customer_client, order, "GIAM10")

    order.refresh_from_db()
    assert order.price == Decimal("45000.00")


def test_inactive_coupon_does_not_change_order(customer_client, order):
    Coupon.objects.create(code="HETHAN", discount=50, active=False)

    apply_coupon(customer_client, order, "HETHAN")

    order.refresh_from_db()
    assert order.price == Decimal("50000.00")


# ---------- Cash on delivery ----------


def test_cash_on_delivery_places_order_and_empties_cart(customer_client, customer, product, add_to_cart):
    # TC_05
    add_to_cart(customer_client, product)
    submit_shipping_info(customer_client)
    order = CartOrder.objects.get(user=customer)

    response = customer_client.post(reverse("core:place-cod-order", args=[order.oid]))

    order.refresh_from_db()
    assert response.url == reverse("core:payment-completed", args=[order.oid])
    assert (order.payment_method, order.paid_status) == ("cod", False)  # paid on delivery
    assert "cart_data_obj" not in customer_client.session


def test_customer_cannot_place_order_of_another_customer(client, order, django_user_model, password):
    stranger = django_user_model.objects.create_user(
        email="nguoila@example.com", username="nguoila", password=password
    )
    client.force_login(stranger)

    response = client.post(reverse("core:place-cod-order", args=[order.oid]))

    order.refresh_from_db()
    assert response.url == reverse("core:checkout-info")
    assert order.payment_method == "online"  # unchanged


# ---------- Payment completed page (L-8) ----------


def test_payment_completed_page_does_not_mark_unpaid_order_as_paid(customer_client, order):
    response = customer_client.get(reverse("core:payment-completed", args=[order.oid]))

    order.refresh_from_db()
    assert order.paid_status is False
    assert response.url == reverse("core:checkout", args=[order.oid])  # not the success page


def test_payment_completed_page_shows_online_order_confirmed_by_vnpay(customer_client, order):
    order.paid_status = True  # as vnpay_return leaves it after checking the signature
    order.save()

    response = customer_client.get(reverse("core:payment-completed", args=[order.oid]))

    assert response.status_code == 200


def test_payment_completed_page_shows_unpaid_cod_order(customer_client, customer, product, add_to_cart):
    add_to_cart(customer_client, product)
    submit_shipping_info(customer_client)
    order = CartOrder.objects.get(user=customer)
    customer_client.post(reverse("core:place-cod-order", args=[order.oid]))

    response = customer_client.get(reverse("core:payment-completed", args=[order.oid]))

    order.refresh_from_db()
    assert response.status_code == 200  # COD is paid on delivery, so unpaid is expected here
    assert order.paid_status is False
