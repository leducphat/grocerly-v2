"""
Read-only product API tests (/api/v1/products/, UC-16).

The API is deliberately outside i18n_patterns, so its paths carry no /vi/ or
/en/ prefix (see CLAUDE.md section 7).
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import Product

pytestmark = pytest.mark.django_db


def list_products(client):
    return client.get(reverse("store_api:api-products")).json()


def test_product_api_returns_published_products(client, product):
    titles = [p["title"] for p in list_products(client)]

    assert titles == [product.title]


def test_product_api_does_not_return_product_hidden_from_store(client, product):
    # L-10: the API used to filter on `status`, which the shop never writes, so
    # a product hidden from every store page was still served here.
    product.product_status = "disabled"
    product.save()

    assert list_products(client) == []


def test_product_api_does_not_return_product_out_of_stock(client, product):
    product.stock_count = 0
    product.save()

    assert list_products(client) == []


def test_product_api_does_not_return_product_awaiting_review(client):
    Product.objects.create(title="Táo Fuji", price=Decimal("50000.00"), stock_count=5)  # in_review

    assert list_products(client) == []
