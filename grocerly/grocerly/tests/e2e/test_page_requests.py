"""
What the page scripts send, in a real browser (UC-06, UC-08, UC-12, UC-17, UC-19;
L-18, L-19, L-21, L-23, L-26, D-043, D-044).

The pytest tests check what the server answers to a request written by hand. These
check what only a browser shows: that the requests of the page really carry the CSRF
token and survive the language prefix, and that a double click sends one request.
"""

import contextlib
import json
import time

import pytest
from django.urls import reverse
from playwright.sync_api import Error as PlaywrightError

from core.models import Product, Vendor, Wishlist
from useradmin import views as useradmin_views
from userauths.models import ContactUs

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def add_button(page, product):
    return page.locator(f'.add-to-cart-btn[data-index="{product.id}"]').first


def click_twice(locator):
    """Two clicks in the same instant, as a double click on a slow connection."""
    locator.evaluate("button => { button.click(); button.click(); }")


def cart_quantity(page, live_server, product):
    """The quantity the cart page shows for `product`, or None if it is not in the cart."""
    page.goto(live_server.url + reverse("core:cart"))
    box = page.locator(f'.cart-qty-input[data-product="{product.id}"]')
    return int(box.input_value()) if box.count() else None


def posts_to(page, url_name):
    """The list that collects every POST the page sends to `url_name`."""
    posts = []
    page.on("request", lambda r: posts.append(r) if r.method == "POST" and reverse(url_name) in r.url else None)
    return posts


# ---------- Requests of the shop pages carry the token (L-19) ----------


@pytest.mark.parametrize("language", ["vi", "en"])
def test_add_button_puts_the_product_in_the_cart(sign_in, customer, product, live_server, language):
    page = sign_in(customer).new_page()
    page.goto(f"{live_server.url}/{language}/")

    with page.expect_response(lambda r: "add-to-cart" in r.url) as answer:
        add_button(page, product).dispatch_event("click")

    assert answer.value.status == 200
    assert answer.value.request.method == "POST"
    assert cart_quantity(page, live_server, product) == 1


def test_guest_can_add_to_cart(browser, product, live_server):
    context = browser.new_context()
    page = context.new_page()
    page.goto(live_server.url + reverse("core:index"))

    with page.expect_response(lambda r: "add-to-cart" in r.url) as answer:
        add_button(page, product).dispatch_event("click")

    assert answer.value.status == 200
    context.close()


def test_mini_cart_link_keeps_the_english_site(browser, product, live_server):
    # L-35. A guest who opened an /en/ link has no language cookie yet. A link without
    # the prefix is redirected by LocaleMiddleware to the default language, so the
    # product page would open in Vietnamese.
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{live_server.url}/en/")

    with page.expect_response(lambda r: "add-to-cart" in r.url):
        add_button(page, product).dispatch_event("click")

    link = page.locator(".shopping-cart-title h4 a").first
    assert link.get_attribute("href").startswith("/en/")
    context.close()


def test_cart_page_changes_quantity_and_removes_a_line(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    with page.expect_response(lambda r: "add-to-cart" in r.url):
        add_button(page, product).dispatch_event("click")
    page.goto(live_server.url + reverse("core:cart"))

    with page.expect_response(lambda r: "update-cart" in r.url) as update:
        page.locator(f'.cart-qty-input[data-product="{product.id}"]').fill("4")
    with page.expect_response(lambda r: "delete-from-cart" in r.url) as delete:
        page.locator(f'.delete-product[data-product="{product.id}"]').dispatch_event("click")

    assert (update.value.status, delete.value.status) == (200, 200)
    assert page.locator(".mini-cart-count").first.text_content().strip() == "0"


def test_heart_and_wishlist_page_change_the_wishlist(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))

    with page.expect_response(lambda r: "add-to-wishlist" in r.url) as added:
        page.locator(f'.add-to-wishlist[data-product-id="{product.id}"]').first.dispatch_event("click")
    assert added.value.status == 200
    assert Wishlist.objects.filter(user=customer).count() == 1

    page.goto(live_server.url + reverse("core:wishlist"))
    with page.expect_response(lambda r: "remove-from-wishlist" in r.url) as removed:
        page.locator(".delete-wishlist-product").first.click()

    assert removed.value.status == 200
    assert not Wishlist.objects.filter(user=customer).exists()


def test_add_button_says_so_when_the_server_refuses_and_works_again(sign_in, customer, product, live_server):
    # A page left open across a sign-in holds an old token, so the POST gets 403.
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    alerts = []
    page.on("dialog", lambda d: (alerts.append(d.message), d.accept()))
    page.route("**/add-to-cart/", lambda route: route.fulfill(status=403, body="Forbidden"))

    add_button(page, product).dispatch_event("click")
    page.wait_for_timeout(500)

    assert len(alerts) == 1
    assert add_button(page, product).is_enabled()


# ---------- Other sites (L-19) ----------


def test_link_on_another_site_cannot_change_the_cart(sign_in, other_site, customer, product, live_server):
    context = sign_in(customer)
    url = live_server.url + reverse("core:add-to-cart") + f"?id={product.id}&qty=9"
    start = other_site(context, f'<a id="go" href="{url}">Xem khuyen mai</a>')
    statuses = []
    context.on("response", lambda r: statuses.append(r.status) if r.url == url else None)
    page = context.new_page()
    page.goto(start)

    # As in test_delete_product.py: Chrome swaps the empty 405 for its own error page.
    with contextlib.suppress(PlaywrightError):
        page.click("#go")
        page.wait_for_timeout(1000)

    assert statuses == [405]
    assert cart_quantity(context.new_page(), live_server, product) is None


def test_form_posted_from_another_site_cannot_change_the_cart(sign_in, other_site, customer, product, live_server):
    context = sign_in(customer)
    url = live_server.url + reverse("core:add-to-cart")
    fields = f'<input name="id" value="{product.id}"><input name="qty" value="9">'
    start = other_site(context, f'<form id="f" method="post" action="{url}">{fields}</form><script>f.submit()</script>')
    statuses = []
    context.on("response", lambda r: statuses.append(r.status) if r.url == url else None)
    page = context.new_page()

    page.goto(start)
    page.wait_for_timeout(1000)

    assert statuses == [403]
    assert cart_quantity(context.new_page(), live_server, product) is None


# ---------- A double click counts once (L-18, L-21, L-23) ----------


def test_double_click_on_add_counts_once(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    posts = posts_to(page, "core:add-to-cart")

    with page.expect_response(lambda r: "add-to-cart" in r.url):
        click_twice(add_button(page, product))
    page.wait_for_timeout(300)

    assert len(posts) == 1
    assert cart_quantity(page, live_server, product) == 1


def test_add_button_adds_again_once_the_first_click_is_answered(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))

    for _ in range(2):
        with page.expect_response(lambda r: "add-to-cart" in r.url):
            add_button(page, product).dispatch_event("click")
        page.wait_for_timeout(300)

    assert cart_quantity(page, live_server, product) == 2


def chat_proposes(page, product, qty):
    """Answer the chat window the way the server does when Gemini proposes to add `qty`."""
    return chat_answers(page, {
        "reply": f"Thêm {qty}x {product.title}?",
        "action": "confirm_add_cart",
        "product": {"id": str(product.id), "pid": product.p_id, "title": product.title, "qty": qty},
    })


def chat_answers(page, answer):
    """Send a chat message, have the server answer `answer`, return the buttons shown."""
    page.route(
        "**/api/v1/chat/",
        lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(answer)),
    )
    page.evaluate("toggleChatbot()")
    page.fill("#chat-input", "them hang")
    page.keyboard.press("Enter")
    return page.locator("#chat-messages button.btn-success")


def test_chat_confirm_button_adds_once_and_reports_the_total(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    with page.expect_response(lambda r: "add-to-cart" in r.url):
        add_button(page, product).dispatch_event("click")
    posts = posts_to(page, "core:add-to-cart")

    button = chat_proposes(page, product, 2)
    with page.expect_response(lambda r: "add-to-cart" in r.url):
        click_twice(button)
    page.wait_for_function("() => document.querySelector('#chat-messages').innerText.includes('3x')")

    assert len(posts) == 1
    assert button.is_disabled()
    assert page.locator(".mini-cart-count").first.text_content().strip() == "1"
    assert cart_quantity(page, live_server, product) == 3


def test_chat_add_shows_in_the_mini_cart(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))

    with page.expect_response(lambda r: "add-to-cart" in r.url):
        chat_proposes(page, product, 1).click()
    page.wait_for_timeout(300)

    assert page.locator(".mini-cart-count").first.text_content().strip() == "1"


def test_chat_says_when_the_stock_cut_the_total_down(sign_in, customer, product, live_server):
    Product.objects.filter(pk=product.pk).update(stock_count=2)
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    with page.expect_response(lambda r: "add-to-cart" in r.url):
        add_button(page, product).dispatch_event("click")

    with page.expect_response(lambda r: "add-to-cart" in r.url):
        chat_proposes(page, product, 2).click()

    page.wait_for_function("() => document.querySelector('#chat-messages').innerText.includes('Kho chỉ còn 2')")


def test_chat_confirm_button_works_again_after_a_failed_request(sign_in, customer, product, live_server):
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    button = chat_proposes(page, product, 1)
    page.route("**/add-to-cart/", lambda route: route.abort())

    button.click()
    page.wait_for_timeout(500)

    assert button.is_enabled()


def test_chat_choice_adds_only_the_product_clicked(sign_in, customer, product, live_server):
    # SRS AC-17.3, D-048: several products match, one button each. Clicking one
    # picks and confirms it, and turns every button of that reply off.
    other = Product.objects.create(
        title="Cà rốt baby", category=product.category, price=product.price,
        stock_count=10, product_status="published",
    )
    page = sign_in(customer).new_page()
    page.goto(live_server.url + reverse("core:index"))
    posts = posts_to(page, "core:add-to-cart")
    choices = [
        {"id": str(p.id), "pid": p.p_id, "title": p.title, "qty": 2, "label": f"Thêm 2x {p.title}"}
        for p in (product, other)
    ]
    buttons = chat_answers(page, {"reply": "Bạn chọn một:", "action": "choose_product", "choices": choices})

    with page.expect_response(lambda r: "add-to-cart" in r.url):
        buttons.nth(1).click()
    # The buttons hold "2x Cà rốt baby" too, so wait for the cart's own answer.
    page.wait_for_function("() => document.querySelector('#chat-messages').innerText.includes('đã có 2x Cà rốt baby')")

    assert buttons.count() == 2
    assert buttons.nth(0).is_disabled() and buttons.nth(1).is_disabled()
    assert len(posts) == 1
    assert cart_quantity(page, live_server, other) == 2
    assert cart_quantity(page, live_server, product) is None


def test_double_click_on_create_product_makes_one_product(sign_in, staff, product, live_server, monkeypatch):
    real_redirect = useradmin_views.redirect

    def slow_redirect(*args):
        time.sleep(0.6)
        return real_redirect(*args)

    monkeypatch.setattr(useradmin_views, "redirect", slow_redirect)
    vendor = Vendor.objects.create(name="HTX Rau Đà Lạt")
    page = sign_in(staff).new_page()
    page.goto(live_server.url + reverse("useradmin:dashboard-add-products"))
    page.fill('[name="title"]', "Cà chua bi")
    page.fill('textarea[name="description"]', "Cà chua bi Đà Lạt")
    page.fill('[name="price"]', "30000")
    page.fill('[name="old_price"]', "35000")
    page.fill('[name="stock_count"]', "5")
    page.select_option('[name="vendor"]', str(vendor.id))
    page.select_option('[name="category"]', str(product.category_id))

    # The answer is held back, as a slow image upload does, and the clicks have a gap:
    # two submits in one instant are merged by the browser and would pass without the
    # lock, and without the delay the page is gone before the second click.
    with page.expect_navigation():
        page.get_by_role("button", name="Tạo sản phẩm").evaluate(
            "button => { button.click(); setTimeout(() => button.click(), 150); }"
        )
    page.wait_for_timeout(1000)

    assert Product.objects.filter(title="Cà chua bi").count() == 1


def test_back_button_finds_the_create_button_on_again(sign_in, staff, product, live_server):
    page = sign_in(staff).new_page()
    page.goto(live_server.url + reverse("useradmin:dashboard-add-products"))
    button = page.get_by_role("button", name="Tạo sản phẩm")
    page.evaluate("document.querySelector('form[enctype]').noValidate = true")

    with page.expect_navigation():
        button.click()
    page.go_back()

    assert button.is_enabled()


def test_double_click_on_contact_form_stores_one_message(browser, live_server, db):
    context = browser.new_context()
    page = context.new_page()
    page.goto(live_server.url + reverse("core:contact"))
    page.fill("#full_name", "Nguyễn Văn A")
    page.fill("#email", "khach@example.com")
    page.fill("#phone", "0900000000")
    page.fill("#subject", "Hỏi đơn hàng")
    page.fill("#message", "Đơn của tôi tới khi nào?")

    with page.expect_response(lambda r: "ajax-contact-form" in r.url) as answer:
        click_twice(page.locator('form#contact-form-ajax button[type="submit"]'))
    page.wait_for_timeout(300)

    assert answer.value.status == 200
    assert ContactUs.objects.count() == 1
    context.close()


# ---------- Stock box of the staff page (L-26) ----------


def test_stock_box_saves_with_the_csrf_check_on(sign_in, staff, product, live_server):
    page = sign_in(staff).new_page()
    page.goto(live_server.url + reverse("useradmin:dashboard-products"))
    page.fill(f".stock-input-{product.p_id}", "3")

    with page.expect_response(lambda r: "update_stock" in r.url) as answer:
        page.locator(f'.update-stock-btn[data-pid="{product.p_id}"]').click()

    assert answer.value.status == 200
    product.refresh_from_db()
    assert product.stock_count == 3
