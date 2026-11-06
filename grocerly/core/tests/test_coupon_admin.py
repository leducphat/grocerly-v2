"""
Coupons in the Django admin (UC-21, L-68).

A coupon takes `discount` percent off the order (core/views.py, checkout). Nothing
bounded the number, so a coupon of 150 made the order price negative and one of 0 or
less did nothing or raised the price. The admin form now takes 1 to 100 only.
"""

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from core.models import Coupon

pytestmark = pytest.mark.django_db


def add_coupon(client, discount):
    return client.post(reverse("admin:core_coupon_add"), {"code": "GIAM", "discount": discount, "active": "on"})


@pytest.mark.parametrize("discount", ["0", "-10", "101", "150"])
def test_admin_cannot_save_coupon_outside_1_to_100_percent(superuser_client, discount):
    response = add_coupon(superuser_client, discount)

    assert response.status_code == 200  # the form comes back with the error
    assert not Coupon.all_objects.exists()


@pytest.mark.parametrize("discount", ["1", "100"])
def test_admin_saves_coupon_at_the_edges_of_the_range(superuser_client, discount):
    add_coupon(superuser_client, discount)

    assert Coupon.objects.get().discount == int(discount)


def test_coupon_outside_the_range_fails_model_validation():
    with pytest.raises(ValidationError):
        Coupon(code="GIAM", discount=150).full_clean()
