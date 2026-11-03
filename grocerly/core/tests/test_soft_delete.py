"""
Deleting a category, vendor, product or coupon (FR-A-02, UC-19, UC-24, L-28): the
row stays, so it can be restored, and customers stop seeing it.

SoftDeleteModel used to override delete() on the QuerySet only. obj.delete() ran
Django's own delete and removed the row for good, and that is what the Delete button
in /useradmin/ and on a Django admin edit page both call.

A deleted row is still reachable through a foreign key, because Django follows a
foreign key with a plain manager and not with `objects`. That is why the pages that
start from a wishlist line or a product card are tested here too (D-041).
"""

from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from core.models import Coupon, Product, ProductImage, ProductReview, Vendor, Wishlist

pytestmark = pytest.mark.django_db


@pytest.fixture(params=["category", "vendor", "product", "coupon"])
def row(request, product, vendor):
    """One row of each of the four models that inherit SoftDeleteModel."""
    return {
        "category": product.category,
        "vendor": vendor,
        "product": product,
        "coupon": Coupon.objects.create(code="GIAM10", discount=10, active=True),
    }[request.param]


@pytest.fixture
def superuser_client(client, django_user_model, password):
    """The test client, signed in to the Django admin. pytest-django's own admin_client
    cannot be used: it creates the user without the `username` this model requires."""
    superuser = django_user_model.objects.create_superuser(
        email="quantri@example.com", username="quantri", password=password
    )
    client.force_login(superuser)
    return client


@pytest.fixture
def vendor_product(product, vendor):
    """`product`, sold by `vendor`."""
    product.vendor = vendor
    product.save()
    return product


@pytest.fixture
def other_product(db):
    """A second published product, so a wishlist can hold one line that stays."""
    return Product.objects.create(
        title="Bắp cải tím", price=Decimal("15000.00"), stock_count=5, product_status="published"
    )


@pytest.fixture
def wishlist_line(customer, product):
    """`product` in the wishlist of `customer`."""
    return Wishlist.objects.create(user=customer, product=product)


# ---------- The row stays ----------


def test_delete_hides_the_row_and_keeps_it(row):
    row.delete()

    model = type(row)
    assert not model.objects.filter(pk=row.pk).exists()
    stored = model.all_objects.get(pk=row.pk)
    assert stored.is_deleted is True
    assert stored.deleted_at is not None


def test_deleted_row_can_be_restored(row):
    row.delete()

    type(row).all_objects.get(pk=row.pk).restore()

    assert type(row).objects.filter(pk=row.pk).exists()


def test_deleting_a_row_again_keeps_its_first_deleted_at(row):
    # The Django admin lists deleted rows, so their Delete button can be pressed again.
    model = type(row)
    row.delete()
    first_deleted_at = model.all_objects.get(pk=row.pk).deleted_at

    model.all_objects.get(pk=row.pk).delete()

    assert model.all_objects.get(pk=row.pk).deleted_at == first_deleted_at


def test_hard_delete_still_removes_the_row(row):
    row.hard_delete()

    assert not type(row).all_objects.filter(pk=row.pk).exists()


def test_deleting_product_keeps_its_images_and_reviews(product, customer):
    image = ProductImage.objects.create(product=product)
    review = ProductReview.objects.create(product=product, user=customer, review="Ngọt", rating=5)

    product.delete()

    assert ProductImage.objects.filter(pk=image.pk).exists()
    review.refresh_from_db()
    assert review.product_id == product.pk


# ---------- A vendor takes its products with it ----------


def test_deleting_vendor_hides_its_products(vendor_product, vendor):
    vendor.delete()

    assert not Product.objects.filter(pk=vendor_product.pk).exists()


def test_restoring_vendor_brings_back_the_products_deleted_with_it(vendor_product, vendor):
    vendor.delete()

    Vendor.all_objects.get(pk=vendor.pk).restore()

    assert Product.objects.filter(pk=vendor_product.pk).exists()


def test_restoring_vendor_deleted_twice_still_brings_back_its_products(vendor_product, vendor):
    # restore() finds the products by the vendor's deleted_at, so a second delete
    # must not move it.
    vendor.delete()
    Vendor.all_objects.get(pk=vendor.pk).delete()

    Vendor.all_objects.get(pk=vendor.pk).restore()

    assert Product.objects.filter(pk=vendor_product.pk).exists()


def test_restoring_vendor_leaves_products_deleted_before_it(vendor_product, vendor):
    vendor_product.delete()
    vendor.delete()

    Vendor.all_objects.get(pk=vendor.pk).restore()

    assert not Product.objects.filter(pk=vendor_product.pk).exists()


# ---------- Django admin ----------


def test_django_admin_delete_button_keeps_the_row(superuser_client, product):
    url = reverse("admin:core_product_delete", args=[product.pk])

    response = superuser_client.post(url, {"post": "yes"})

    assert response.status_code == 302
    assert Product.all_objects.get(pk=product.pk).is_deleted is True


def test_django_admin_restore_action_brings_back_the_products_of_a_vendor(superuser_client, vendor_product, vendor):
    vendor.delete()

    superuser_client.post(
        reverse("admin:core_vendor_changelist"),
        {"action": "restore_selected", "_selected_action": [vendor.pk]},
    )

    assert Vendor.objects.filter(pk=vendor.pk).exists()
    assert Product.objects.filter(pk=vendor_product.pk).exists()


@pytest.mark.xfail(reason="L-36: the bulk soft-delete action of the admin skips Vendor.soft_delete, products stay on sale")
@pytest.mark.parametrize("action", ["soft_delete_selected", "delete_selected"])
def test_django_admin_bulk_delete_of_a_vendor_hides_their_products(superuser_client, vendor_product, vendor, action):
    # Both actions of the vendor list run a single UPDATE on the vendors, so the
    # cascade in Vendor.soft_delete never runs, unlike the Delete button of one vendor.
    # The products stay on sale while their vendor page answers 404.
    superuser_client.post(
        reverse("admin:core_vendor_changelist"),
        {"action": action, "_selected_action": [vendor.pk], "post": "yes"},
    )

    assert not Vendor.objects.filter(pk=vendor.pk).exists()
    assert not Product.objects.filter(pk=vendor_product.pk).exists()


# ---------- What customers see ----------


def test_page_of_deleted_product_answers_404(client, product):
    product.delete()

    response = client.get(reverse("core:product-detail", args=[product.p_id]))

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("url_name", "params"),
    [("core:index", {}), ("core:product-list", {}), ("core:search", {"q": "Cà rốt"})],
)
def test_deleted_product_leaves_the_listing_pages(client, product, url_name, params):
    product.delete()

    response = client.get(reverse(url_name), params)

    assert response.status_code == 200
    assert product.p_id not in response.content.decode()


def test_page_of_deleted_category_answers_404(client, product):
    product.category.delete()

    response = client.get(reverse("core:category-product-list", args=[product.category.c_id]))

    assert response.status_code == 404


def test_page_of_deleted_vendor_answers_404(client, vendor):
    vendor.delete()

    response = client.get(reverse("core:vendor-detail", args=[vendor.v_id]))

    assert response.status_code == 404


@pytest.mark.parametrize("url_name", ["core:category-product-list", "core:vendor-detail"])
def test_page_of_unknown_category_or_vendor_answers_404(client, db, url_name):
    response = client.get(reverse(url_name, args=["khongcoma"]))

    assert response.status_code == 404


def test_products_of_deleted_category_stay_on_sale(client, product):
    # Only the category goes; a product is deleted on its own (D-041).
    product.category.delete()

    response = client.get(reverse("core:index"))

    assert response.status_code == 200
    assert product.p_id in response.content.decode()


# ---------- Wishlist ----------


def test_wishlist_page_leaves_out_deleted_product(customer_client, product, wishlist_line):
    product.delete()

    response = customer_client.get(reverse("core:wishlist"))

    assert response.status_code == 200
    assert product.p_id not in response.content.decode()


def test_wishlist_page_survives_line_that_lost_its_product(customer_client, customer):
    # The old Delete button emptied the foreign key of the line (SET_NULL), and the
    # template cannot build a link to an empty product. Such lines may be on the host.
    Wishlist.objects.create(user=customer, product=None)

    response = customer_client.get(reverse("core:wishlist"))

    assert response.status_code == 200


def test_wishlist_count_leaves_out_deleted_product(customer_client, product, wishlist_line):
    product.delete()

    response = customer_client.get(reverse("core:wishlist"))

    assert response.context["wishlist_count"] == 0
    assert list(response.context["wishlist_product_ids"]) == []


def test_removing_from_wishlist_leaves_out_deleted_product(
    customer_client, customer, product, wishlist_line, other_product
):
    kept = Wishlist.objects.create(user=customer, product=other_product)
    product.delete()

    response = customer_client.post(reverse("core:remove-from-wishlist"), {"id": kept.id})

    body = response.json()
    assert body["total_wishlist_items"] == 0
    assert product.p_id not in body["data"]


def test_adding_deleted_product_to_wishlist_is_refused_with_a_reason(customer_client, customer, product):
    # The page was opened before staff deleted the product, so its heart still works.
    product.delete()

    response = customer_client.post(reverse("core:add-to-wishlist"), {"id": product.id})

    body = response.json()
    assert body["bool"] is False
    assert body["error"] == "Sản phẩm này không còn bán nữa."
    assert not Wishlist.objects.filter(user=customer).exists()


@pytest.mark.parametrize("bad_id", ["999999", "abc", ""])
def test_add_to_wishlist_refuses_unknown_product(customer_client, bad_id):
    response = customer_client.post(reverse("core:add-to-wishlist"), {"id": bad_id})

    assert response.json()["bool"] is False


def test_adding_to_wishlist_counts_only_products_still_on_sale(
    customer_client, product, wishlist_line, other_product
):
    product.delete()

    response = customer_client.post(reverse("core:add-to-wishlist"), {"id": other_product.id})

    assert response.json()["total_wishlist_items"] == 1


@pytest.mark.parametrize("url_name", ["core:add-to-wishlist", "core:remove-from-wishlist"])
def test_wishlist_cannot_be_changed_by_get_request(customer_client, customer, product, wishlist_line, url_name):
    target = product.id if url_name == "core:add-to-wishlist" else wishlist_line.id

    response = customer_client.get(reverse(url_name), {"id": target})

    assert response.status_code == 405
    assert Wishlist.objects.filter(user=customer).count() == 1


@pytest.mark.parametrize("url_name", ["core:add-to-wishlist", "core:remove-from-wishlist"])
def test_wishlist_post_without_csrf_token_is_rejected(customer, product, wishlist_line, url_name):
    client = Client(enforce_csrf_checks=True)
    client.force_login(customer)
    target = product.id if url_name == "core:add-to-wishlist" else wishlist_line.id

    response = client.post(reverse(url_name), {"id": target})

    assert response.status_code == 403
    assert Wishlist.objects.filter(user=customer).count() == 1
