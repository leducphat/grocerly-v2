"""
Forms whose answer only a browser shows (L-49, L-50, UC-08, UC-14).

The review form posts to an endpoint that answers JSON. A test client sees the JSON
either way; only a browser shows whether the customer stays on the product page or
lands on the raw JSON.
"""

import pytest
from django import forms
from django.urls import reverse
from django.utils import translation

from core.models import CartOrder, CartOrderItem, ProductReview
from userauths.models import ContactUs

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def received_product(customer, product):
    """`product`, in a delivered order of `customer`: the review form is offered (UC-14)."""
    order = CartOrder.objects.create(
        user=customer, price=product.price, email=customer.email, product_status="delivered"
    )
    CartOrderItem.objects.create(
        order=order, invoice_no=f"INVOICE_NO-{order.id}", product=product,
        item=product.title, quantity=1, price=product.price, total=product.price,
    )
    return product


def open_review_form(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    product_url = live_server.url + reverse("core:product-detail", args=[product.p_id])
    page.goto(product_url)
    page.click("#Reviews-tab")
    return page, product_url


def test_sent_review_keeps_the_customer_on_the_product_page(sign_in, customer, received_product, live_server):
    page, product_url = open_review_form(sign_in, customer, received_product, live_server)

    page.fill("#commentForm textarea[name=review]", "Cà rốt ngọt, giòn")
    page.select_option("#commentForm select[name=rating]", "5")
    with page.expect_response(lambda r: "ajax-add-review" in r.url):
        page.click("#commentForm [type=submit]")

    assert page.url == product_url
    assert ProductReview.objects.filter(product=received_product, user=customer).exists()


def test_empty_review_shows_the_error_on_the_product_page(sign_in, customer, received_product, live_server):
    page, product_url = open_review_form(sign_in, customer, received_product, live_server)
    with translation.override("vi"):
        required = str(forms.Field.default_error_messages["required"])

    page.select_option("#commentForm select[name=rating]", "5")
    # The browser would refuse the empty box by itself; the server check is what is tested.
    page.eval_on_selector("#commentForm", "form => form.noValidate = true")
    with page.expect_response(lambda r: "ajax-add-review" in r.url):
        page.click("#commentForm [type=submit]")

    assert page.url == product_url
    assert page.get_by_text(required).first.is_visible()


def test_rejected_contact_form_shows_the_error_under_the_box(browser, live_server):
    # L-50: the server refuses an empty form with 400; the script of
    # partials/base.html puts each error under its box instead of a network alert.
    page = browser.new_context().new_page()
    page.goto(live_server.url + reverse("core:contact"))
    with translation.override("vi"):
        required = str(forms.Field.default_error_messages["required"])

    page.eval_on_selector("form#contact-form-ajax", "form => form.noValidate = true")
    with page.expect_response(lambda r: "ajax-contact-form" in r.url) as answer:
        page.click("form#contact-form-ajax [type=submit]")

    assert answer.value.status == 400
    error = page.locator("#full_name + .text-danger")
    error.wait_for()
    assert error.inner_text() == required
    assert not ContactUs.objects.exists()
