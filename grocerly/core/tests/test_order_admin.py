"""
Orders in the Django admin (UC-25, CN-28).

SRS.md §6.1: the admin may not delete an order for good, the orders are kept for
the accounts. The staff dashboard has no delete button for orders (CN-22); the
Django admin still offers both the Delete button and the "Delete selected" action.
"""

import pytest
from django.urls import reverse

from core.models import CartOrder

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(reason="L-40: CartOrderAdmin allows deleting orders, against UC-25")
@pytest.mark.parametrize("way", ["delete_button", "delete_selected"])
def test_django_admin_cannot_delete_an_order(superuser_client, order, way):
    if way == "delete_button":
        url = reverse("admin:core_cartorder_delete", args=[order.pk])
        superuser_client.post(url, {"post": "yes"})
    else:
        superuser_client.post(
            reverse("admin:core_cartorder_changelist"),
            {"action": "delete_selected", "_selected_action": [order.pk], "post": "yes"},
        )

    assert CartOrder.objects.filter(pk=order.pk).exists()
