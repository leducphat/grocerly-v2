"""
Statistics tests (UC-26, CN-20): which orders the staff dashboard and the shop
page count as revenue, and who may open the dashboard.

SRS.md §6.1: revenue counts the orders that are paid and not cancelled. A VNPay
order that was paid and then cancelled keeps `paid_status=True`, because the
refund happens outside the system (D-033) - so looking at `paid_status` alone
would still count its money.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

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


def test_shop_page_links_each_product_to_its_edit_page(staff_client, staff, product):
    """Review of PR #23: the store page linked products to the customer product page,
    which RestrictStaffMiddleware sends staff away from; it links to the edit page."""
    product.user = staff
    product.save()

    page = staff_client.get(reverse("useradmin:shop_page")).content.decode()

    assert reverse("useradmin:dashboard-edit-products", args=[product.p_id]) in page
    assert reverse("core:product-detail", args=[product.p_id]) not in page


def test_product_list_links_each_product_to_its_edit_page(staff_client, product):
    """Review of PR #24: /useradmin/products/ linked every product, drafts included, to
    the customer product page, which sends staff away and since L-66 answers 404 for a
    product off sale. Same fix as the store page above."""
    product.product_status = "draft"
    product.save()

    page = staff_client.get(reverse("useradmin:dashboard-products")).content.decode()

    assert reverse("useradmin:dashboard-edit-products", args=[product.p_id]) in page
    assert reverse("core:product-detail", args=[product.p_id]) not in page


def a_year_ago(order):
    """Move `order` to the same month of last year (order_date is auto_now_add)."""
    now = timezone.now()
    CartOrder.objects.filter(pk=order.pk).update(
        order_date=now.replace(year=now.year - 1, day=min(now.day, 28))
    )


def test_monthly_revenue_leaves_out_the_same_month_of_last_year(staff_client, customer):
    # UC-26: the dashboard shows the revenue of the current month.
    paid_order(customer, "75000.00")
    a_year_ago(paid_order(customer, "50000.00"))

    response = staff_client.get(reverse("useradmin:dashboard"))

    assert response.context["monthly_revenue"]["price"] == Decimal("75000.00")


def test_revenue_chart_does_not_add_up_the_same_month_of_two_years(staff_client, customer):
    # UC-26: one point of the revenue-by-month chart is one month, not the sum of
    # that month over every year.
    paid_order(customer, "75000.00")
    a_year_ago(paid_order(customer, "50000.00"))

    response = staff_client.get(reverse("useradmin:dashboard"))

    assert 125000.0 not in response.context["rev_total"]


def test_revenue_chart_names_each_month_with_its_year(staff_client, customer):
    # L-76: with two years on the chart, "Tháng 11" alone would appear twice.
    paid_order(customer, "75000.00")
    a_year_ago(paid_order(customer, "50000.00"))
    this_year = timezone.localdate().year

    response = staff_client.get(reverse("useradmin:dashboard"))

    labels = response.context["rev_month"]
    assert len(labels) == 2
    assert str(this_year - 1) in labels[0]
    assert str(this_year) in labels[1]


# ---------- who may open the dashboard (AC-26.3) ----------


def test_customer_cannot_open_the_dashboard(customer_client):
    response = customer_client.get(reverse("useradmin:dashboard"))

    assert response.status_code == 302
    assert response.url == reverse("userauths:sign-in")


def test_anonymous_visitor_cannot_open_the_dashboard(client):
    response = client.get(reverse("useradmin:dashboard"))

    assert response.status_code == 302
    assert response.url == reverse("userauths:sign-in")
