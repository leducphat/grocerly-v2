"""
Fixtures shared by the tests of every app. See docs/DECISIONS.md D-018.

pytest loads this file automatically; tests receive a fixture by naming it as an
argument, e.g. `def test_x(customer_client, product): ...`.
"""

from decimal import Decimal

import pytest
from django.conf import settings

from core.models import Category, Product


def pytest_configure(config):
    # Guard for D-002: stop before any test runs if the suite is not using the
    # throw-away SQLite database of grocerly/settings_test.py — for example
    # `pytest --ds=grocerly.settings`, which would read the database from .env.
    engine = settings.DATABASES["default"]["ENGINE"]
    if engine != "django.db.backends.sqlite3":
        raise pytest.UsageError(
            f"Tests must run with grocerly.settings_test (SQLite), not with {engine}."
        )


@pytest.fixture
def password():
    """Password of every test account; passes AUTH_PASSWORD_VALIDATORS."""
    return "Grocerly#2026-test"


@pytest.fixture
def customer(db, django_user_model, password):
    """A signed-up customer (not staff)."""
    return django_user_model.objects.create_user(
        email="khachhang@example.com", username="khachhang", password=password
    )


@pytest.fixture
def customer_client(client, customer):
    """The Django test client, signed in as `customer`."""
    client.force_login(customer)
    return client


@pytest.fixture
def product(db):
    """A published, in-stock product: 25,000 VND, 10 left."""
    category = Category.objects.create(title="Rau củ")
    return Product.objects.create(
        title="Cà rốt Đà Lạt",
        category=category,
        price=Decimal("25000.00"),
        stock_count=10,
        in_stock=True,
        status=True,
        product_status="published",
    )
