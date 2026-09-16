"""
VNPay tests (UC-09, CN-11). Nothing reaches VNPay: the tests build VNPay's replies
themselves and sign them with the fake secret of grocerly/settings_test.py.
"""

import hashlib
import hmac
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def vnpay_reply(order, response_code="00", amount=None):
    """The parameters VNPay sends back; "00" means the payment succeeded."""
    if amount is None:
        amount = int(order.price) * 100  # VNPay counts in VND x 100
    return {
        "vnp_TxnRef": f"{order.oid}-1758000000",
        "vnp_ResponseCode": response_code,
        "vnp_Amount": str(amount),
    }


def sign(params, secret):
    """Add vnp_SecureHash as VNPay does: HMAC-SHA512 of the sorted, URL-encoded parameters.
    Written independently of core/vnpay.py so the test does not reuse the code it checks.

    Simplified on purpose: core/vnpay.py also ignores keys not starting with "vnp_"
    and empty values. Every parameter built by vnpay_reply() starts with "vnp_" and is
    non-empty, so the result is the same."""
    query = urlencode(sorted(params.items()))
    digest = hmac.new(secret.encode(), query.encode(), hashlib.sha512).hexdigest()
    return {**params, "vnp_SecureHash": digest}


def test_payment_sends_order_total_times_100_to_vnpay(customer_client, order):
    response = customer_client.get(reverse("core:vnpay_payment", args=[order.oid]))

    assert response.status_code == 302
    sent = parse_qs(urlparse(response.url).query)
    assert sent["vnp_Amount"] == ["5000000"]  # 50,000 VND; VNPay expects amount x 100
    assert sent["vnp_TxnRef"][0].startswith(f"{order.oid}-")


def test_vnpay_return_with_valid_signature_marks_order_paid(client, order, settings):
    reply = sign(vnpay_reply(order), settings.VNPAY_HASH_SECRET)

    response = client.get(reverse("core:vnpay_return"), reply)

    order.refresh_from_db()
    assert response.url == reverse("core:payment-completed", args=[order.oid])
    assert order.paid_status is True


def test_vnpay_return_with_forged_signature_does_not_mark_order_paid(client, order):
    reply = sign(vnpay_reply(order), "not-the-real-secret")

    response = client.get(reverse("core:vnpay_return"), reply)

    order.refresh_from_db()
    assert response.url == reverse("core:payment-failed")
    assert order.paid_status is False


def test_vnpay_return_with_cancelled_payment_does_not_mark_order_paid(client, order, settings):
    reply = sign(vnpay_reply(order, response_code="24"), settings.VNPAY_HASH_SECRET)  # 24: customer cancelled

    response = client.get(reverse("core:vnpay_return"), reply)

    order.refresh_from_db()
    assert response.url == reverse("core:payment-failed")
    assert order.paid_status is False


def test_vnpay_ipn_rejects_amount_different_from_order_total(client, order, settings):
    reply = sign(vnpay_reply(order, amount=100), settings.VNPAY_HASH_SECRET)

    response = client.get(reverse("core:vnpay_ipn"), reply)

    order.refresh_from_db()
    assert response.json()["RspCode"] == "04"  # invalid amount
    assert order.paid_status is False
