"""
Search page and product filter (UC-05, CN-06).

The three search boxes of the site always send `q`, empty or not. A link or a typed
URL without it reached search_view with q=None, and the filter title__icontains=None
answered 500 (L-77, seen on the host on 18/11/2026).

The filter on /products/ asks filter_product through AJAX and gets the cards back
as HTML in `data`, with their number in `count`.
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import Category, Product

pytestmark = pytest.mark.django_db


def test_search_with_empty_query_answers_200(client, product):
    response = client.get(reverse("core:search"), {"q": ""})

    assert response.status_code == 200


def test_search_without_query_parameter_answers_200(client, product):
    response = client.get(reverse("core:search"))

    assert response.status_code == 200


# ---------- the filter of /products/ (AC-5.2) ----------


@pytest.fixture
def three_categories(db):
    """Two products in "Rau", one in "Trái cây", one in "Thịt", at different prices."""
    rau, trai_cay, thit = (Category.objects.create(title=t) for t in ("Rau", "Trái cây", "Thịt"))
    for title, category, price in [
        ("Cải ngọt", rau, "20000"),
        ("Bông cải", rau, "80000"),
        ("Cam sành", trai_cay, "30000"),
        ("Ba chỉ", thit, "25000"),
    ]:
        Product.objects.create(
            title=title, category=category, price=Decimal(price),
            stock_count=10, product_status="published",
        )
    return rau, trai_cay, thit


def filtered(client, **params):
    answer = client.get(reverse("core:filter-product"), params).json()
    return answer["count"], answer["data"]


def test_filter_by_two_categories_returns_the_products_of_both(client, three_categories):
    """AC-5.2: several categories give their union."""
    rau, trai_cay, _ = three_categories

    count, html = filtered(client, category=[rau.id, trai_cay.id])

    assert count == 3
    assert all(title in html for title in ("Cải ngọt", "Bông cải", "Cam sành"))
    assert "Ba chỉ" not in html


def test_filter_by_categories_and_price_returns_what_meets_both(client, three_categories):
    """AC-5.2: categories with a price range give the intersection of the two."""
    rau, trai_cay, _ = three_categories

    count, html = filtered(client, category=[rau.id, trai_cay.id], min_price=10000, max_price=50000)

    assert count == 2
    assert "Cải ngọt" in html and "Cam sành" in html
    assert "Bông cải" not in html  # right category, price too high
    assert "Ba chỉ" not in html  # price in range, wrong category

