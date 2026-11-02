"""
Deleting a product in a real browser (UC-19, UC-24, L-28, L-29, D-041).

The pytest tests in useradmin/tests check what the server answers. These check what
only a browser decides: that the confirm() question is really asked, that Chrome
sends the session cookie with a link from another site, and what a customer sees on
a page that was opened before the product was deleted.
"""

import contextlib

import pytest
from django.urls import reverse
from playwright.sync_api import Error as PlaywrightError

from core.models import Product, Wishlist

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def state(product):
    """What the database holds for `product`: on sale, soft deleted, or gone."""
    row = Product.all_objects.filter(pk=product.pk).first()
    if row is None:
        return "gone"
    return "soft deleted" if row.is_deleted else "on sale"


def delete_button(page, product):
    return page.locator(f'form[action*="{product.p_id}"] button')


def test_delete_button_asks_first_and_cancel_keeps_the_product(sign_in, staff, product, live_server):
    page = sign_in(staff).new_page()
    questions = []
    page.on("dialog", lambda d: (questions.append(d.message), d.dismiss()))
    page.goto(live_server.url + reverse("useradmin:dashboard-products"))

    delete_button(page, product).click()
    page.wait_for_timeout(500)

    assert questions == ["Xóa sản phẩm này?"]
    assert state(product) == "on sale"


def test_confirming_the_question_soft_deletes_the_product(sign_in, staff, product, live_server):
    page = sign_in(staff).new_page()
    page.on("dialog", lambda d: d.accept())
    page.goto(live_server.url + reverse("useradmin:dashboard-products"))

    with page.expect_navigation():
        delete_button(page, product).click()

    assert state(product) == "soft deleted"
    assert product.p_id not in page.content()


def test_link_on_another_site_cannot_delete_a_product(sign_in, other_site, staff, product, live_server):
    # Chrome sends the session cookie when a link from another site is followed, so a
    # delete URL that answered GET was a link anyone could plant (L-29).
    context = sign_in(staff)
    delete_url = live_server.url + reverse("useradmin:dashboard-delete-products", args=[product.p_id])
    start = other_site(context, f'<a id="go" href="{delete_url}">Xem khuyen mai</a>')
    statuses = []
    context.on("response", lambda r: statuses.append(r.status) if r.url == delete_url else None)
    page = context.new_page()
    page.goto(start)

    # Chrome replaces the empty 405 answer with its own error page, and Playwright
    # reports that as an error; the status is read from the response event instead.
    with contextlib.suppress(PlaywrightError):
        page.click("#go")
        page.wait_for_timeout(1000)

    assert statuses == [405]
    assert state(product) == "on sale"


def test_form_posted_from_another_site_cannot_delete_a_product(sign_in, other_site, staff, product, live_server):
    context = sign_in(staff)
    delete_url = live_server.url + reverse("useradmin:dashboard-delete-products", args=[product.p_id])
    start = other_site(
        context,
        f'<form id="f" method="post" action="{delete_url}"></form><script>f.submit()</script>',
    )
    statuses = []
    context.on("response", lambda r: statuses.append(r.status) if r.url == delete_url else None)
    page = context.new_page()

    page.goto(start)
    page.wait_for_timeout(1000)

    assert statuses == [403]
    assert state(product) == "on sale"


def test_heart_of_a_product_deleted_meanwhile_says_it_is_gone(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    product.delete()  # staff deletes it while the customer still has the page open
    messages = []
    page.on("dialog", lambda d: (messages.append(d.message), d.accept()))

    # The heart only shows on hover, so the click is sent to it directly.
    page.locator(f'.add-to-wishlist[data-product-id="{product.id}"]').first.dispatch_event("click")
    page.wait_for_timeout(1000)

    assert messages == ["Sản phẩm này không còn bán nữa."]
    assert not Wishlist.objects.filter(user=customer).exists()


def test_wishlist_page_does_not_break_when_its_product_is_deleted(sign_in, customer, product, live_server):
    Wishlist.objects.create(user=customer, product=product)
    product.delete()
    page = sign_in(customer).new_page()

    response = page.goto(live_server.url + reverse("core:wishlist"))

    assert response.status == 200
    assert product.p_id not in page.content()
