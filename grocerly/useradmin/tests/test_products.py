"""
Adding and editing products in /useradmin/ (UC-19, L-27): a product must have a
category and a vendor, and the server decides that, not the browser.
"""

import re
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import translation

from core.models import Category, Product, ProductImage, ProductReview, Vendor

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


# ---------- Deleting extra images on the edit page (UC-19, CN-21) ----------
# The edit page has a hidden "delete_images" checkbox under each extra image; the
# x button ticks it. edit_product deletes the ticked ids after the form is saved.


def images_of(product):
    return set(ProductImage.objects.filter(product=product).values_list("id", flat=True))


def test_edit_page_offers_a_delete_box_for_each_extra_image(staff_client, stocked_product):
    first = ProductImage.objects.create(product=stocked_product)
    second = ProductImage.objects.create(product=stocked_product)

    page = staff_client.get(reverse(EDIT_URL, args=[stocked_product.p_id])).content.decode()

    for image in (first, second):
        assert f'name="delete_images" value="{image.id}"' in page


def test_edit_product_deletes_the_chosen_image_and_keeps_the_others(staff_client, stocked_product, category, vendor):
    chosen = ProductImage.objects.create(product=stocked_product)
    kept = ProductImage.objects.create(product=stocked_product)
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    response = staff_client.post(url, product_form(category, vendor, delete_images=[chosen.id]))

    assert response.url == reverse("useradmin:dashboard-products")
    assert images_of(stocked_product) == {kept.id}


def test_edit_product_does_not_delete_an_image_of_another_product(staff_client, stocked_product, category, vendor):
    # A tampered form may send any id; only this product's own images may go.
    other = Product.objects.create(title="Ổi ruột đỏ", category=category, vendor=vendor, price=Decimal("20000.00"))
    other_image = ProductImage.objects.create(product=other)
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    staff_client.post(url, product_form(category, vendor, delete_images=[other_image.id]))

    assert images_of(other) == {other_image.id}


def test_edit_product_ignores_image_ids_that_are_not_numbers(staff_client, stocked_product, category, vendor):
    # An empty or non-numeric value used to raise ValueError in the id__in filter.
    kept = ProductImage.objects.create(product=stocked_product)
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    response = staff_client.post(url, product_form(category, vendor, delete_images=["", "abc", "1 OR 1=1"]))

    assert response.url == reverse("useradmin:dashboard-products")
    assert images_of(stocked_product) == {kept.id}


def test_rejected_edit_form_deletes_no_image(staff_client, stocked_product, category, vendor):
    # Nothing of a rejected form is saved, the ticked images included.
    image = ProductImage.objects.create(product=stocked_product)
    url = reverse(EDIT_URL, args=[stocked_product.p_id])

    response = staff_client.post(url, product_form(category, vendor, category="", delete_images=[image.id]))

    assert response.status_code == 200
    assert images_of(stocked_product) == {image.id}


# ---------- Deleting a product (L-28, L-29, D-041) ----------


def delete_url(product):
    return reverse("useradmin:dashboard-delete-products", args=[product.p_id])


def still_on_sale(product):
    return Product.objects.filter(pk=product.pk).exists()


def test_delete_button_hides_the_product_and_keeps_its_row(staff_client, stocked_product):
    response = staff_client.post(delete_url(stocked_product))

    assert response.url == reverse("useradmin:dashboard-products")
    assert not still_on_sale(stocked_product)
    assert Product.all_objects.get(pk=stocked_product.pk).is_deleted is True


def test_get_request_does_not_delete_product(staff_client, stocked_product):
    # A link on another site reaches this URL with the staff's cookie (L-29).
    response = staff_client.get(delete_url(stocked_product))

    assert response.status_code == 405
    assert still_on_sale(stocked_product)


def test_delete_without_csrf_token_is_rejected(staff, stocked_product):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)

    response = client.post(delete_url(stocked_product))

    assert response.status_code == 403
    assert still_on_sale(stocked_product)


def test_delete_form_carries_the_csrf_token_it_needs(staff, stocked_product):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff)
    html = client.get(reverse("useradmin:dashboard-products")).content.decode()
    form = html.split(f'action="{delete_url(stocked_product)}"')[1].split("</form>")[0]
    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form).group(1)

    response = client.post(delete_url(stocked_product), {"csrfmiddlewaretoken": token})

    assert response.status_code == 302
    assert not still_on_sale(stocked_product)


def test_customer_cannot_delete_product(customer_client, stocked_product):
    response = customer_client.post(delete_url(stocked_product))

    assert response.url == reverse("userauths:sign-in")
    assert still_on_sale(stocked_product)


def test_anonymous_visitor_cannot_delete_product(client, stocked_product):
    response = client.post(delete_url(stocked_product))

    assert response.url == reverse("userauths:sign-in")
    assert still_on_sale(stocked_product)


def test_deleting_a_product_again_answers_404(staff_client, stocked_product):
    staff_client.post(delete_url(stocked_product))

    response = staff_client.post(delete_url(stocked_product))

    assert response.status_code == 404


def test_product_list_offers_delete_as_a_form_that_asks_first(staff_client, stocked_product):
    html = staff_client.get(reverse("useradmin:dashboard-products")).content.decode()

    form = re.search(rf'<form[^>]*action="{delete_url(stocked_product)}"[^>]*>', html).group()
    assert 'method="post"' in form
    assert "Xóa sản phẩm này?" in form
    assert f'href="{delete_url(stocked_product)}"' not in html


def test_edit_page_of_deleted_product_answers_404(staff_client, stocked_product):
    # A second tab, or the Back button, still holds the link.
    staff_client.post(delete_url(stocked_product))

    response = staff_client.get(reverse(EDIT_URL, args=[stocked_product.p_id]))

    assert response.status_code == 404


def test_deleted_product_leaves_the_staff_product_list(staff_client, stocked_product):
    staff_client.post(delete_url(stocked_product))

    html = staff_client.get(reverse("useradmin:dashboard-products")).content.decode()

    assert stocked_product.p_id not in html


def test_reviews_page_still_names_a_deleted_product(staff_client, stocked_product, customer):
    ProductReview.objects.create(product=stocked_product, user=customer, review="Ngọt", rating=5)
    stocked_product.delete()

    response = staff_client.get(reverse("useradmin:reviews"))

    assert response.status_code == 200
    assert stocked_product.title in response.content.decode()


def test_add_and_edit_forms_lock_their_button_on_submit(staff_client, stocked_product):
    # L-21: the script is in useradmin/base.html, the forms opt in with this attribute.
    add_page = staff_client.get(reverse(ADD_URL)).content.decode()
    edit_page = staff_client.get(
        reverse("useradmin:dashboard-edit-products", args=[stocked_product.p_id])
    ).content.decode()

    assert "data-lock-on-submit>" in add_page
    assert "data-lock-on-submit>" in edit_page
