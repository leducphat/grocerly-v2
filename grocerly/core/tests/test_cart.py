"""
Session cart tests (UC-06, CN-08): add, update quantity, remove, cart page total.
"""

from decimal import Decimal

import pytest
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


def test_adding_same_product_again_keeps_one_cart_line(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    response = add_to_cart(client, product, qty=3)

    assert response.json()["totalcartitems"] == 1


def test_update_cart_changes_quantity(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    client.get(reverse("core:update-cart"), {"id": product.id, "qty": 4})

    assert cart_lines(client)[str(product.id)]["qty"] == 4


def test_update_cart_ignores_product_not_in_cart(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    client.get(reverse("core:update-cart"), {"id": 999999, "qty": 4})

    assert list(cart_lines(client)) == [str(product.id)]


def test_delete_from_cart_removes_line(client, product, add_to_cart):
    add_to_cart(client, product, qty=1)

    response = client.get(reverse("core:delete-from-cart"), {"id": product.id})

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


@pytest.mark.xfail(reason="L-7: the server does not check stock when adding to the cart")
def test_add_to_cart_does_not_keep_quantity_above_stock(client, product, add_to_cart):
    add_to_cart(client, product, qty=product.stock_count + 1)

    kept_qty = cart_lines(client).get(str(product.id), {}).get("qty", 0)
    assert kept_qty <= product.stock_count
