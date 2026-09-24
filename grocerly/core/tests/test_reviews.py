"""
Product review tests (UC-14, CN-15): who may rate a product and how often.

SRS.md §6.1 grants the review to the customer who has bought the product; the
view used to accept a review from anyone (L-3 in docs/COMMITMENT.md).
"""

import pytest
from django.urls import reverse

from core.models import ProductReview

pytestmark = pytest.mark.django_db


def post_review(client, product, review="Cà rốt rất tươi", rating=5):
    return client.post(
        reverse("core:ajax-add-review", args=[product.id]),
        {"review": review, "rating": rating},
    )


def test_customer_who_bought_the_product_can_review_it(
    customer_client, product, shipped_order
):
    shipped_order()

    response = post_review(customer_client, product)

    assert response.status_code == 200
    assert ProductReview.objects.filter(product=product).count() == 1


def test_customer_who_received_the_product_can_review_it(
    customer_client, product, shipped_order
):
    """A delivered order is a bought product too - see PLAN.md §6."""
    shipped_order(status="delivered")

    post_review(customer_client, product)

    assert ProductReview.objects.filter(product=product).count() == 1


def test_visitor_who_is_not_signed_in_cannot_review(client, product):
    """L-3: the view took `request.user` without ever checking it."""
    response = post_review(client, product)

    assert reverse("userauths:sign-in") in response.url
    assert ProductReview.objects.count() == 0


def test_customer_who_never_bought_the_product_cannot_review_it(
    customer_client, product
):
    """L-3: the rating of a product should come from someone who received it."""
    response = post_review(customer_client, product)

    assert response.status_code == 403
    assert ProductReview.objects.count() == 0


def test_order_still_on_its_way_does_not_allow_a_review_yet(
    customer_client, product, shipped_order
):
    shipped_order(status="processing")

    response = post_review(customer_client, product)

    assert response.status_code == 403
    assert ProductReview.objects.count() == 0


def test_order_of_another_customer_does_not_allow_a_review(
    customer_client, product, shipped_order, django_user_model, password
):
    other = django_user_model.objects.create_user(
        email="nguoikhac@example.com", username="nguoikhac", password=password
    )
    shipped_order(user=other)

    response = post_review(customer_client, product)

    assert response.status_code == 403
    assert ProductReview.objects.count() == 0


def test_customer_cannot_review_the_same_product_twice(
    customer_client, product, shipped_order
):
    shipped_order()
    post_review(customer_client, product)

    response = post_review(customer_client, product, review="Đánh giá lần hai")

    assert response.status_code == 403
    assert ProductReview.objects.filter(product=product).count() == 1


def test_review_without_a_rating_is_rejected(customer_client, product, shipped_order):
    shipped_order()

    response = post_review(customer_client, product, rating="")

    assert response.status_code == 400
    assert ProductReview.objects.count() == 0


def test_review_form_is_hidden_from_a_customer_who_did_not_buy_the_product(
    customer_client, product
):
    """SRS §6.1 asks for the button to be disabled, not only for the post to fail."""
    response = customer_client.get(
        reverse("core:product-detail", args=[product.p_id])
    )

    assert response.context["make_review"] is False
