"""
Product review tests (UC-14, CN-15): who may rate a product and how often, what
the product page makes of the ratings, and who may change a review.

SRS.md §6.1 grants the review to the customer who has bought the product; the
view used to accept a review from anyone (L-3 in docs/ISSUES.md).
"""

import pytest
from django.urls import reverse

from core import urls as core_urls
from core.models import CartOrderItem, Product, ProductReview

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


def test_cancelled_order_does_not_allow_a_review(
    customer_client, product, shipped_order
):
    """An order cancelled on its way was never received (D-033)."""
    shipped_order(status="cancelled")

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


def test_customer_can_review_product_renamed_after_buying_it(
    customer_client, product, shipped_order
):
    shipped_order()
    product.title = "Cà rốt Đà Lạt loại 1"
    product.save()

    response = post_review(customer_client, product)

    assert response.status_code == 200


def test_buying_one_product_does_not_allow_reviewing_another_with_the_same_title(
    customer_client, product, shipped_order
):
    shipped_order()
    same_title = Product.objects.create(
        title=product.title, category=product.category, price=product.price,
        stock_count=5, product_status="published",
    )

    response = post_review(customer_client, same_title)

    assert response.status_code == 403


def test_order_line_without_a_product_gives_no_right_to_review(
    customer_client, product, shipped_order
):
    # A line the migration could not link stays unlinked; the title is not a way back.
    shipped_order()
    CartOrderItem.objects.update(product=None)

    response = post_review(customer_client, product)

    assert response.status_code == 403


# ---------- the rating on the product page (AC-4.2) ----------


def test_product_page_rating_counts_only_the_reviews_of_that_product(client, product, customer):
    other = Product.objects.create(
        title="Bắp cải", category=product.category, price=product.price,
        stock_count=5, product_status="published",
    )
    for rating in (5, 3):
        ProductReview.objects.create(product=product, user=customer, review="Ngon", rating=rating)
    for rating in (1, 1):
        ProductReview.objects.create(product=other, user=customer, review="Dập", rating=rating)

    response = client.get(reverse("core:product-detail", args=[product.p_id]))

    assert response.context["average_rating"]["rating"] == 4
    shares = [response.context[f"rating_{stars}"] for stars in (5, 4, 3, 2, 1)]
    assert shares == [50, 0, 50, 0, 0]


# ---------- the customer only adds; changing a review is moderation (AC-14.3) ----------


def test_shop_has_no_route_for_the_customer_to_edit_or_delete_a_review():
    """The one review route of the shop is the one that adds a review."""
    review_routes = {route.name for route in core_urls.urlpatterns if "review" in (route.name or "")}

    assert review_routes == {"ajax-add-review"}


def test_customer_cannot_open_their_own_review_in_django_admin(customer_client, customer, product):
    review = ProductReview.objects.create(product=product, user=customer, review="Ngon", rating=5)

    response = customer_client.get(reverse("admin:core_productreview_change", args=[review.pk]))

    assert response.status_code == 302
    assert reverse("admin:login") in response.url


def test_administrator_can_delete_a_review_in_django_admin(client, django_user_model, password, customer, product):
    admin = django_user_model.objects.create_superuser(
        email="quantri@example.com", username="quantri", password=password
    )
    review = ProductReview.objects.create(product=product, user=customer, review="Spam", rating=1)
    client.force_login(admin)

    client.post(reverse("admin:core_productreview_delete", args=[review.pk]), {"post": "yes"})

    assert not ProductReview.objects.filter(pk=review.pk).exists()
