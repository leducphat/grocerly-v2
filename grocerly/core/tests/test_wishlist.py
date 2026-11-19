"""
Removing a product from the wishlist (UC-12, CN-13).

The wishlist page sends the remove request by AJAX and redraws the list only when
the answer carries `bool: true` (templates/core/wishlist.html). remove_wishlist left
that key out, so the row and the counter stayed on screen until a reload although
the line was gone from the database (L-78, seen on the host on 18/11/2026).
"""

import pytest
from django.urls import reverse

from core.models import Wishlist

pytestmark = pytest.mark.django_db


@pytest.fixture
def wishlist_line(customer, product):
    return Wishlist.objects.create(user=customer, product=product)


def test_remove_from_wishlist_deletes_the_line(customer_client, wishlist_line):
    customer_client.post(reverse("core:remove-from-wishlist"), {"id": wishlist_line.id})

    assert not Wishlist.objects.filter(id=wishlist_line.id).exists()


def test_remove_from_wishlist_answer_tells_the_page_to_redraw(customer_client, wishlist_line):
    response = customer_client.post(reverse("core:remove-from-wishlist"), {"id": wishlist_line.id})

    body = response.json()
    assert body["bool"] is True
    assert body["total_wishlist_items"] == 0
