"""
Search page (UC-05, CN-06).

The three search boxes of the site always send `q`, empty or not. A link or a typed
URL without it reached search_view with q=None, and the filter title__icontains=None
answered 500 (L-77, seen on the host on 18/11/2026).
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_search_with_empty_query_answers_200(client, product):
    response = client.get(reverse("core:search"), {"q": ""})

    assert response.status_code == 200


@pytest.mark.xfail(reason="L-77: search_view filters title__icontains=None when q is missing")
def test_search_without_query_parameter_answers_200(client, product):
    response = client.get(reverse("core:search"))

    assert response.status_code == 200
