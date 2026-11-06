"""
Products the shop has taken off sale stay out of the customer's pages (UC-03, UC-04,
UC-24, L-66), and a deleted category leaves no dead link on a card (UC-23, L-67).

Only a product in the status 'published' is on sale. The list pages already filter on
it, but three places did not: the product page itself, the category tabs of the home
page (c.products.all) and the product counts next to each category or vendor.
"""

import pytest
from django.urls import reverse
from django.utils import translation

from core.models import Product

pytestmark = pytest.mark.django_db

HIDDEN_STATUSES = ["draft", "disabled", "in_review", "rejected"]


@pytest.fixture(params=HIDDEN_STATUSES)
def hidden_product(request, product):
    """`product`, moved out of 'published' by the admin."""
    product.product_status = request.param
    product.save()
    return product


def test_page_of_product_off_sale_answers_404(client, hidden_product):
    response = client.get(reverse("core:product-detail", args=[hidden_product.p_id]))

    assert response.status_code == 404


def test_page_of_product_on_sale_still_opens(client, product):
    response = client.get(reverse("core:product-detail", args=[product.p_id]))

    assert response.status_code == 200


def test_category_tab_of_home_page_leaves_out_product_off_sale(client, hidden_product):
    response = client.get(reverse("core:index"))

    assert response.status_code == 200
    assert hidden_product.p_id not in response.content.decode()


def test_category_tab_of_home_page_shows_product_on_sale(client, product):
    response = client.get(reverse("core:index"))

    tab = response.content.decode().split(f'id="tab-{product.category.c_id}"')[1]
    assert product.p_id in tab


def test_category_count_leaves_out_product_off_sale(product):
    Product.objects.create(title="Cà rốt nháp", category=product.category, price=1, product_status="draft")

    assert list(product.category.on_sale_products()) == [product]


def test_vendor_count_leaves_out_product_off_sale(product, vendor):
    product.vendor = vendor
    product.save()
    Product.objects.create(title="Hàng tắt", vendor=vendor, price=1, product_status="disabled")

    assert list(vendor.on_sale_products()) == [product]


def test_category_list_page_counts_only_products_on_sale(client, product):
    Product.objects.create(title="Cà rốt nháp", category=product.category, price=1, product_status="draft")
    # The request stays inside override(), as in test_order_history.py: a request to
    # /en/ would otherwise leave the tests after this one in English.
    with translation.override("en"):
        page = client.get(reverse("core:category-list")).content.decode()

    assert "1 product" in page
    assert "2 products" not in page


# ---------- Card of a product whose category was deleted (L-67) ----------

LISTING_PAGES = [
    ("core:index", [], {}),
    ("core:product-list", [], {}),
    ("core:search", [], {"q": "Cà rốt"}),
    ("core:tags", ["rau-cu"], {}),
]


@pytest.mark.parametrize("url_name, args, params", LISTING_PAGES)
def test_card_has_no_link_to_a_deleted_category(client, product, url_name, args, params):
    product.tags.add("rau-cu")
    category_url = reverse("core:category-product-list", args=[product.category.c_id])
    product.category.delete()

    response = client.get(reverse(url_name, args=args), params)

    page = response.content.decode()
    assert response.status_code == 200
    assert product.p_id in page  # the product stays on sale (D-041)
    assert category_url not in page


def test_product_page_has_no_link_to_a_deleted_category(client, product):
    category_url = reverse("core:category-product-list", args=[product.category.c_id])
    product.category.delete()

    response = client.get(reverse("core:product-detail", args=[product.p_id]))

    assert response.status_code == 200
    assert category_url not in response.content.decode()


def test_category_sidebar_of_vendor_page_counts_only_products_on_sale(client, product, vendor):
    # Review of PR #24: the vendor page sidebar still counted c.products.all.
    product.vendor = vendor
    product.save()
    Product.objects.create(title="Cà rốt nháp", category=product.category, vendor=vendor, price=1, product_status="draft")

    page = client.get(reverse("core:vendor-detail", args=[vendor.v_id])).content.decode()

    assert '<span class="count">1</span>' in page
