"""
Adding and editing products in /useradmin/ (UC-19, L-27): a product must have a
category and a vendor, and the server decides that, not the browser.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import translation

from core.models import Category, Product, Vendor

pytestmark = pytest.mark.django_db

ADD_URL = "useradmin:dashboard-add-products"
EDIT_URL = "useradmin:dashboard-edit-products"

NO_CATEGORY_MESSAGE = "Vui lòng chọn danh mục"
NO_VENDOR_MESSAGE = "Vui lòng chọn nhà cung cấp"


@pytest.fixture
def category(db):
    return Category.objects.create(title="Trái cây")


@pytest.fixture
def stocked_product(staff, category, vendor):
    return Product.objects.create(
        title="Xoài cát",
        user=staff,
        category=category,
        vendor=vendor,
        price=Decimal("50000.00"),
        old_price=Decimal("60000.00"),
        stock_count=3,
        product_status="published",
    )


def product_form(category, vendor, /, **changes):
    """What the browser sends when the staff fills in the form. The `/` lets a test
    write product_form(category, vendor, category="") to empty that field."""
    data = {
        "title": "Cà chua bi",
        "description": "Cà chua bi Đà Lạt",
        "price": "30000",
        "old_price": "35000",
        "stock_count": "5",
        "category": category.id,
        "vendor": vendor.id,
    }
    return {**data, **changes}


# ---------- Adding a product ----------


def test_add_product_with_category_and_vendor_publishes_it(staff_client, category, vendor):
    response = staff_client.post(reverse(ADD_URL), product_form(category, vendor))

    assert response.url == reverse("useradmin:dashboard-products")
    product = Product.objects.get(title="Cà chua bi")
    assert (product.category, product.vendor) == (category, vendor)
    assert product.product_status == "published"


def test_add_product_without_category_creates_nothing(staff_client, category, vendor):
    response = staff_client.post(reverse(ADD_URL), product_form(category, vendor, category=""))

    assert response.status_code == 200  # the form again, not a redirect
    assert NO_CATEGORY_MESSAGE in response.content.decode()
    assert Product.objects.count() == 0


def test_add_product_without_vendor_creates_nothing(staff_client, category, vendor):
    """The view used to pick the first vendor by itself: a wrong guess, or no guess
    at all while the store had no vendors yet."""
    response = staff_client.post(reverse(ADD_URL), product_form(category, vendor, vendor=""))

    assert response.status_code == 200
    assert NO_VENDOR_MESSAGE in response.content.decode()
    assert Product.objects.count() == 0


def test_add_product_with_neither_reports_both(staff_client, category, vendor):
    response = staff_client.post(reverse(ADD_URL), product_form(category, vendor, category="", vendor=""))

    page = response.content.decode()
    assert NO_CATEGORY_MESSAGE in page
    assert NO_VENDOR_MESSAGE in page
    assert Product.objects.count() == 0


def test_add_product_error_follows_page_language(staff_client, category, vendor):
    # override() as in core/tests/test_order_history.py: a request to /en/ would
    # otherwise leave the whole test thread in English.
    with translation.override("en"):
        response = staff_client.post(reverse(ADD_URL), product_form(category, vendor, category=""))

    assert "Please choose a category" in response.content.decode()


def test_rejected_form_keeps_what_the_staff_typed(staff_client, category, vendor):
    response = staff_client.post(reverse(ADD_URL), product_form(category, vendor, category=""))

    assert 'value="Cà chua bi"' in response.content.decode()


@pytest.mark.parametrize("field", ["category", "vendor"])
def test_add_product_rejects_choice_that_does_not_exist(staff_client, category, vendor, field):
    data = product_form(category, vendor, **{field: 999999})

    staff_client.post(reverse(ADD_URL), data)

    assert Product.objects.count() == 0


def test_add_product_rejects_soft_deleted_category(staff_client, category, vendor):
    category.soft_delete()

    staff_client.post(reverse(ADD_URL), product_form(category, vendor))

    assert Product.objects.count() == 0


def test_add_product_rejects_soft_deleted_vendor(staff_client, category, vendor):
    vendor.soft_delete()

    staff_client.post(reverse(ADD_URL), product_form(category, vendor))

    assert Product.objects.count() == 0


def test_customer_cannot_add_product(customer_client, category, vendor):
    response = customer_client.post(reverse(ADD_URL), product_form(category, vendor))

    assert response.status_code == 302
    assert Product.objects.count() == 0


# ---------- Editing a product ----------


@pytest.mark.parametrize(
    ("emptied", "message"),
    [("category", NO_CATEGORY_MESSAGE), ("vendor", NO_VENDOR_MESSAGE)],
)
def test_edit_product_cannot_empty_category_or_vendor(staff_client, stocked_product, category, vendor, emptied, message):
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    response = staff_client.post(url, product_form(category, vendor, title="Tên mới", **{emptied: ""}))

    assert response.status_code == 200
    assert message in response.content.decode()
    stocked_product.refresh_from_db()
    assert stocked_product.title == "Xoài cát"  # nothing of the rejected form was saved
    assert (stocked_product.category, stocked_product.vendor) == (category, vendor)


def test_edit_product_saves_a_valid_change(staff_client, stocked_product, category, vendor):
    other_vendor = Vendor.objects.create(name="Nông trại Củ Chi")
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    response = staff_client.post(url, product_form(category, other_vendor))

    assert response.url == reverse("useradmin:dashboard-products")
    stocked_product.refresh_from_db()
    assert stocked_product.vendor == other_vendor


def test_product_left_without_category_can_be_repaired_on_the_edit_page(staff_client, stocked_product, category, vendor):
    """A product saved before the form required these two still opens for editing."""
    stocked_product.category = None
    stocked_product.vendor = None
    stocked_product.save()
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    opened = staff_client.get(url)
    staff_client.post(url, product_form(category, vendor))

    assert opened.status_code == 200
    stocked_product.refresh_from_db()
    assert (stocked_product.category, stocked_product.vendor) == (category, vendor)
