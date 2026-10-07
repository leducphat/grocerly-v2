"""
Statistics tests (UC-26, CN-20): which orders the staff dashboard and the shop
page count as revenue.

SRS.md §6.1: revenue counts the orders that are paid and not cancelled. A VNPay
order that was paid and then cancelled keeps `paid_status=True`, because the
refund happens outside the system (D-033) - so looking at `paid_status` alone
would still count its money.
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import CartOrder, CartOrderItem

pytestmark = pytest.mark.django_db


def paid_order(customer, price, status="processing"):
    """An online order of `customer` that VNPay has confirmed as paid."""
    return CartOrder.objects.create(
        user=customer,
        price=Decimal(price),
        payment_method="online",
        paid_status=True,
        product_status=status,
    )


def test_dashboard_revenue_counts_paid_orders_only(staff_client, customer):
    paid_order(customer, "75000.00")
    CartOrder.objects.create(user=customer, price=Decimal("20000.00"))  # not paid

    response = staff_client.get(reverse("useradmin:dashboard"))

    assert response.context["revenue"]["price"] == Decimal("75000.00")


def test_dashboard_revenue_leaves_out_cancelled_orders(staff_client, customer):
    paid_order(customer, "75000.00")
    paid_order(customer, "50000.00", status="cancelled")  # paid, then cancelled

    response = staff_client.get(reverse("useradmin:dashboard"))

    assert response.context["revenue"]["price"] == Decimal("75000.00")
    assert response.context["rev_total"] == [75000.0]  # the revenue-by-month chart


def test_dashboard_still_lists_cancelled_orders(staff_client, customer):
    """Cancelling takes the money out of the revenue, not the order out of the list."""
    paid_order(customer, "50000.00", status="cancelled")

    response = staff_client.get(reverse("useradmin:dashboard"))

    assert response.context["total_orders_count"].count() == 1


def test_shop_page_revenue_and_items_sold_leave_out_cancelled_orders(staff_client, customer):
    kept = paid_order(customer, "75000.00")
    cancelled = paid_order(customer, "50000.00", status="cancelled")
    CartOrderItem.objects.create(order=kept, item="Cà rốt Đà Lạt", quantity=3)
    CartOrderItem.objects.create(order=cancelled, item="Cà rốt Đà Lạt", quantity=2)

    response = staff_client.get(reverse("useradmin:shop_page"))

    assert response.context["revenue"]["price"] == Decimal("75000.00")
    assert response.context["total_sales"]["qty"] == 3  # the 2 cancelled units are not sold
