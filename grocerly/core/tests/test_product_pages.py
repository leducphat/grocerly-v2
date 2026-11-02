"""
Pages that list products (UC-03, UC-19, L-27): a product with no category or no
vendor must not take the page down for everyone.

Every product card links to its category and its vendor with {% url %}, and {% url %}
raises NoReverseMatch on an empty argument. One such product made /vi/, /en/ and
/vi/products/ answer 500 on the KLTN host on 30/10/2026. The form no longer lets
staff create one (useradmin/tests/test_products.py), but deleting a category or
vendor for good still leaves products without one (SET_NULL), so the cards have to
cope with it as well.
"""

import re

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

# Each page that shows product cards, with the request that puts the product on it.
LISTING_PAGES = [
    ("core:index", [], {}),
    ("core:product-list", [], {}),
    ("core:search", [], {"q": "Cà rốt"}),
    ("core:tags", ["rau-cu"], {}),
]


@pytest.fixture(params=["no-category", "no-vendor", "neither"])
def incomplete_product(request, product, vendor):
    """`product` with its category, its vendor or both gone.

    featured=True also puts it in the deals block of the home page and of the
    product list, and the tag puts it on the tag page, so every card template runs.
    """
    if request.param == "no-category":
        product.category, product.vendor = None, vendor
    elif request.param == "no-vendor":
        product.vendor = None
    else:
        product.category, product.vendor = None, None
    product.featured = True
    product.save()
    product.tags.add("rau-cu")
    return product


@pytest.fixture
def complete_product(product, vendor):
    """`product` with both links, shown on the same cards as incomplete_product."""
    product.vendor = vendor
    product.featured = True
    product.save()
    product.tags.add("rau-cu")
    return product


@pytest.mark.parametrize(("url_name", "args", "params"), LISTING_PAGES)
def test_incomplete_product_does_not_break_listing_page(client, incomplete_product, url_name, args, params):
    response = client.get(reverse(url_name, args=args), params)

    assert response.status_code == 200
    assert incomplete_product.title in response.content.decode()


def test_incomplete_product_does_not_break_product_filter(client, incomplete_product):
    """The filter on /products/ renders the card template on its own, through AJAX."""
    response = client.get(reverse("core:filter-product"))

    assert response.status_code == 200
    assert incomplete_product.title in response.json()["data"]


def test_incomplete_product_has_its_own_page(client, incomplete_product):
    response = client.get(reverse("core:product-detail", args=[incomplete_product.p_id]))

    assert response.status_code == 200
    assert incomplete_product.title in response.content.decode()


def test_product_without_vendor_does_not_break_category_page(client, product):
    response = client.get(reverse("core:category-product-list", args=[product.category.c_id]))

    assert response.status_code == 200
    assert product.title in response.content.decode()


def test_product_without_category_does_not_break_vendor_page(client, product, vendor):
    product.category = None
    product.vendor = vendor
    product.save()

    response = client.get(reverse("core:vendor-detail", args=[vendor.v_id]))

    assert response.status_code == 200
    assert product.title in response.content.decode()


@pytest.mark.parametrize(("url_name", "args", "params"), LISTING_PAGES)
def test_complete_product_keeps_its_vendor_and_category_links(client, complete_product, url_name, args, params):
    """The guards in the templates must not hide the links of a normal product."""
    category_url = reverse("core:category-product-list", args=[complete_product.category.c_id])
    vendor_url = reverse("core:vendor-detail", args=[complete_product.vendor.v_id])

    page = client.get(reverse(url_name, args=args), params).content.decode()

    # The menu and the sidebar link to categories and vendors too, so these two
    # checks look for the markup of the card, not just for the URL.
    assert re.search(rf'class="product-category">\s*<a href="{category_url}"', page)
    assert f'By <a href="{vendor_url}"' in page


def test_home_page_keeps_the_links_on_every_block_of_cards(client, complete_product):
    """The test above passes as long as one block keeps the link. The product sits in
    three blocks here: all products, the tab of its category, and the deals."""
    category_url = reverse("core:category-product-list", args=[complete_product.category.c_id])
    vendor_url = reverse("core:vendor-detail", args=[complete_product.vendor.v_id])

    page = client.get(reverse("core:index")).content.decode()

    assert len(re.findall(rf'class="product-category">\s*<a href="{category_url}"', page)) == 2  # deals show none
    assert page.count(f'By <a href="{vendor_url}"') == 3


def test_product_list_keeps_the_vendor_link_on_the_deal_card(client, complete_product):
    vendor_url = reverse("core:vendor-detail", args=[complete_product.vendor.v_id])

    page = client.get(reverse("core:product-list")).content.decode()

    assert page.count(f'<a href="{vendor_url}">') == 2  # the product card and the deal
