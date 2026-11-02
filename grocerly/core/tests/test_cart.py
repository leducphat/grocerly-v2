"""
Session cart tests (UC-06, CN-08): add, update quantity, remove, cart page total.
"""

from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from core.models import Product

pytestmark = pytest.mark.django_db


def cart_lines(client):
    """The cart kept in the session: {product id (str): {"qty", "price", ...}}."""
    return client.session.get("cart_data_obj", {})


def test_add_to_cart_puts_product_in_cart(client, product, add_to_cart):
    response = add_to_cart(client, product, qty=2)

    assert response.json()["totalcartitems"] == 1
    line = cart_lines(client)[str(product.id)]
    assert (line["pid"], line["qty"]) == (product.p_id, 2)


def test_cart_line_keeps_product_price_not_price_sent_by_browser(client, product, add_to_cart):
    # L-6: the price in the request is only the one the product page displayed.
    add_to_cart(client, product, price="1000")  # real price: 25,000

    assert cart_lines(client)[str(product.id)]["price"] == str(product.price)


def test_add_to_cart_ignores_unknown_product(client, db):
    response = client.post(reverse("core:add-to-cart"), {"id": 999999, "qty": 1})

    assert response.status_code == 404
    assert cart_lines(client) == {}


def test_cart_drops_line_of_product_taken_off_sale(client, product, add_to_cart):
    add_to_cart(client, product)

    product.soft_delete()
    response = client.get(reverse("core:cart"))

    assert cart_lines(client) == {}
    assert response.url == reverse("core:index")  # nothing left to show


def test_adding_same_product_again_keeps_one_cart_line(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    response = add_to_cart(client, product, qty=3)

    assert response.json()["totalcartitems"] == 1


def test_update_cart_changes_quantity(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    client.post(reverse("core:update-cart"), {"id": product.id, "qty": 4})

    assert cart_lines(client)[str(product.id)]["qty"] == 4


def test_update_cart_ignores_product_not_in_cart(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    client.post(reverse("core:update-cart"), {"id": 999999, "qty": 4})

    assert list(cart_lines(client)) == [str(product.id)]


def test_delete_from_cart_removes_line(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    response = client.post(reverse("core:delete-from-cart"), {"id": product.id})

    assert response.json()["totalcartitems"] == 0
    assert cart_lines(client) == {}


def test_cart_page_with_empty_cart_redirects_home(client):
    response = client.get(reverse("core:cart"))

    assert response.status_code == 302
    assert response.url == reverse("core:index")


def test_cart_page_total_is_sum_of_quantity_times_price(client, product, add_to_cart):
    milk = Product.objects.create(title="Sữa tươi", price=Decimal("32000.00"), stock_count=5)
    add_to_cart(client, product, qty=2)  # 2 x 25,000
    add_to_cart(client, milk, qty=1)  # 1 x 32,000

    response = client.get(reverse("core:cart"))

    assert response.status_code == 200
    assert response.context["cart_total_amount"] == 82000


# ---------- Stock (L-7) ----------


def test_add_to_cart_does_not_keep_quantity_above_stock(client, product, add_to_cart):
    add_to_cart(client, product, qty=product.stock_count + 1)

    kept_qty = cart_lines(client).get(str(product.id), {}).get("qty", 0)
    assert kept_qty <= product.stock_count


def test_add_to_cart_keeps_quantity_equal_to_stock(client, product, add_to_cart):
    # The boundary itself is allowed: ten left means ten can be bought.
    add_to_cart(client, product, qty=product.stock_count)

    assert cart_lines(client)[str(product.id)]["qty"] == product.stock_count


def test_update_cart_does_not_keep_quantity_above_stock(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    client.post(reverse("core:update-cart"), {"id": product.id, "qty": 99})

    assert cart_lines(client)[str(product.id)]["qty"] == product.stock_count


def test_cart_page_total_uses_the_quantity_the_stock_allows(client, product, add_to_cart):
    add_to_cart(client, product, qty=product.stock_count + 5)  # 10 left x 25,000

    response = client.get(reverse("core:cart"))

    assert response.context["cart_total_amount"] == product.price * product.stock_count


def test_cart_drops_line_of_product_that_ran_out_of_stock(client, product, add_to_cart):
    add_to_cart(client, product, qty=2)

    Product.objects.filter(id=product.id).update(stock_count=0)
    response = client.get(reverse("core:cart"))

    assert cart_lines(client) == {}
    assert response.url == reverse("core:index")  # nothing left to show

# ---------- Adding to a line already in the cart (L-18) ----------


def test_adding_product_already_in_cart_adds_to_its_quantity(client, product, add_to_cart):
    # The "Add" button on the home page always sends qty=1, so a line of 3 goes
    # back to 1; asking the assistant for 2 more leaves 2.
    add_to_cart(client, product, qty=3)

    add_to_cart(client, product, qty=2)

    assert cart_lines(client)[str(product.id)]["qty"] == 5


def test_adding_to_a_line_stops_at_the_stock(client, product, add_to_cart):
    add_to_cart(client, product, qty=8)

    response = add_to_cart(client, product, qty=5)

    assert response.json()["data"][str(product.id)]["qty"] == product.stock_count


def test_add_to_cart_answers_the_total_the_customer_asked_for(client, product, add_to_cart):
    # The chat window compares this with the line to say when the stock cut it down.
    add_to_cart(client, product, qty=8)

    response = add_to_cart(client, product, qty=5)

    assert response.json()["wanted_qty"] == 13


def test_minus_sign_in_quantity_cannot_lower_a_line(client, product, add_to_cart):
    # safe_int drops the sign, so "-2" reads as 2 and a line can only grow here.
    add_to_cart(client, product, qty=3)

    add_to_cart(client, product, qty=-2)

    assert cart_lines(client)[str(product.id)]["qty"] == 5


def test_update_cart_sets_the_quantity_instead_of_adding(client, product, add_to_cart):
    add_to_cart(client, product, qty=3)

    client.post(reverse("core:update-cart"), {"id": product.id, "qty": 2})

    assert cart_lines(client)[str(product.id)]["qty"] == 2


# ---------- CSRF (L-19) ----------


def put_in_cart(client, product, qty):
    """Write a cart line straight into the session, without calling a cart view."""
    session = client.session
    session["cart_data_obj"] = {
        str(product.id): {"title": product.title, "qty": qty, "price": str(product.price),
                          "image": "", "pid": product.p_id},
    }
    session.save()


def test_add_to_cart_does_not_accept_get_request(client, product):
    response = client.get(reverse("core:add-to-cart"), {"id": product.id, "qty": 1})

    assert response.status_code == 405
    assert cart_lines(client) == {}


@pytest.mark.parametrize(("url_name", "params"), [("core:update-cart", {"qty": 4}), ("core:delete-from-cart", {})])
def test_cart_line_cannot_be_changed_by_get_request(client, product, url_name, params):
    put_in_cart(client, product, qty=1)

    response = client.get(reverse(url_name), {"id": product.id, **params})

    assert response.status_code == 405
    assert cart_lines(client)[str(product.id)]["qty"] == 1


@pytest.mark.parametrize("url_name", ["core:add-to-cart", "core:update-cart", "core:delete-from-cart"])
def test_cart_post_without_csrf_token_is_rejected(product, url_name):
    # POST alone is not the fix: a form on another site can POST too.
    client = Client(enforce_csrf_checks=True)  # the test client skips CSRF checks by default
    put_in_cart(client, product, qty=1)

    response = client.post(reverse(url_name), {"id": product.id, "qty": 4})

    assert response.status_code == 403
    assert cart_lines(client)[str(product.id)]["qty"] == 1


@pytest.mark.parametrize(
    ("language", "url"),
    [("vi", "/vi/add-to-cart/"), ("en", "/en/add-to-cart/"), ("vi", "/vi/update-cart/"), ("vi", "/vi/delete-from-cart/")],
)
def test_page_scripts_call_cart_urls_with_the_language_prefix(client, language, url):
    # Without the prefix the server answers 302 and the browser turns the POST into a GET.
    page = client.get(f"/{language}/").content.decode()

    assert f"url: '{url}'" in page


def test_page_scripts_send_the_csrf_token_of_the_page(client):
    response = client.get("/vi/")

    assert f"'X-CSRFToken': '{response.context['csrf_token']}'" in response.content.decode()
