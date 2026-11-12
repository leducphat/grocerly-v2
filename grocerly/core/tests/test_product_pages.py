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
    # checks look for the markup of the card, not just for the URL. The word before
    # the vendor link is translated ("By" / "Bởi"), so the second check skips it.
    assert re.search(rf'class="product-category">\s*<a href="{category_url}"', page)
    assert re.search(rf'text-muted">[^<]+<a href="{vendor_url}"', page)


def test_home_page_keeps_the_links_on_every_block_of_cards(client, complete_product):
    """The test above passes as long as one block keeps the link. The product sits in
    three blocks here: all products, the tab of its category, and the deals."""
    category_url = reverse("core:category-product-list", args=[complete_product.category.c_id])
    vendor_url = reverse("core:vendor-detail", args=[complete_product.vendor.v_id])

    page = client.get(reverse("core:index")).content.decode()

    assert len(re.findall(rf'class="product-category">\s*<a href="{category_url}"', page)) == 2  # deals show none
    assert len(re.findall(rf'text-muted">[^<]+<a href="{vendor_url}"', page)) == 3


def test_product_list_keeps_the_vendor_link_on_the_deal_card(client, complete_product):
    vendor_url = reverse("core:vendor-detail", args=[complete_product.vendor.v_id])

    page = client.get(reverse("core:product-list")).content.decode()

    assert page.count(f'<a href="{vendor_url}">') == 2  # the product card and the deal


# --- L-61: the discount shows only when there is one -----------------------------------

# Every page that prints a product's price: the cards above, plus the vendor page,
# the product page (with its related products) and the filter on /products/.
PRICE_PAGES = [*LISTING_PAGES, "vendor-detail", "product-detail", "filter"]
DISCOUNT_LABEL = re.compile(r"-\d+%")


@pytest.fixture
def priced_product(complete_product):
    """`complete_product` and a second product of its category, so the product page
    has a related product to show. Both get the same old price in each test."""
    def _with_old_price(old_price):
        other = type(complete_product).objects.create(
            title="Cà rốt baby", category=complete_product.category, vendor=complete_product.vendor,
            price=complete_product.price, old_price=old_price, stock_count=5,
            in_stock=True, status=True, product_status="published",
        )
        complete_product.old_price = old_price
        complete_product.save()
        return complete_product, other
    return _with_old_price


def price_page(client, page, product):
    if page == "vendor-detail":
        return client.get(reverse("core:vendor-detail", args=[product.vendor.v_id])).content.decode()
    if page == "product-detail":
        return client.get(reverse("core:product-detail", args=[product.p_id])).content.decode()
    if page == "filter":
        return client.get(reverse("core:filter-product")).json()["data"]
    url_name, args, params = page
    return client.get(reverse(url_name, args=args), params).content.decode()


@pytest.mark.parametrize("page", PRICE_PAGES, ids=lambda p: p if isinstance(p, str) else p[0])
@pytest.mark.parametrize("old_price", ["0", "20000"], ids=["no-old-price", "old-price-below-price"])
def test_product_without_a_discount_shows_no_discount(client, priced_product, page, old_price):
    """L-61, UC-03: old_price is 0 by default, and a price raised above the old one
    is no discount either. Before the fix the cards printed "-0%" and a struck-out
    "0 ₫"; the old price was printed on every card whatever its value."""
    product, _ = priced_product(old_price)

    html = price_page(client, page, product)

    assert product.title in html
    assert 'class="old-price' not in html
    assert not DISCOUNT_LABEL.search(html)


@pytest.mark.parametrize("page", PRICE_PAGES, ids=lambda p: p if isinstance(p, str) else p[0])
def test_product_on_sale_still_shows_its_old_price_and_discount(client, priced_product, page):
    """The guard of L-61 must not hide a real discount: 25,000 down from 30,000 is 16%."""
    product, _ = priced_product("30000")

    html = price_page(client, page, product)

    assert 'class="old-price' in html
    assert "30.000 ₫" in html
    assert "-16%" in html
