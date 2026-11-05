"""Every page speaks one language: /vi/ pages in Vietnamese, /en/ pages in English
(CLAUDE.md §7, SRS §6.1, D-056). Traces to the mixed-language defects of P-46:
L-47, L-55, L-56, L-57, L-58 in docs/ISSUES.md.

Two kinds of test live here:

- Tests that read the source. This machine has no GNU gettext, so `makemessages`
  cannot list the strings marked for translation; `marked_strings()` does the same
  job with Django's own `templatize()` (the function `makemessages` runs on each
  template before handing it to xgettext).
- Tests that open the same page at /vi/ and at /en/ and compare the text a visitor
  sees. A text that is identical on both pages was never translated, except names
  and data, which read the same in every language (`SAME_IN_BOTH`).
"""

import ast
import io
import re
import tokenize
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.validators import validate_image_file_extension
from django.db import models
from django.urls import reverse
from django.utils import translation
from django.utils.translation.template import templatize

from core.models import CartOrder, CartOrderItem, ProductReview

BASE_DIR = Path(settings.BASE_DIR)
APPS = ["core", "userauths", "useradmin", "store_api", "grocerly"]

# Letters only Vietnamese uses; a text holding one of them is Vietnamese.
VIETNAMESE = re.compile(
    r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I
)


# --- strings marked for translation in the source ----------------------------------

GETTEXT_CALLS = {"_", "gettext", "gettext_lazy", "gettext_noop", "pgettext", "pgettext_lazy",
                 "ngettext", "ngettext_lazy"}


def _literal(parts):
    """The value of one call argument if it is a plain string literal, else None.
    "abc" "def" written next to each other is one string in Python."""
    if parts and all(p.type == tokenize.STRING and not p.string.lower().startswith(("f", "rf", "fr"))
                     for p in parts):
        return "".join(ast.literal_eval(p.string) for p in parts)
    return None


def _gettext_calls(code, origin):
    """Yield (function, [arguments], where) for each gettext call in `code`.

    tokenize splits Python code into names, brackets and string literals, so the
    call _("Save") is the name `_`, then "(", then the string "Save". An argument
    that is not a plain literal (a variable, an f-string) comes back as None.
    """
    tokens = [t for t in tokenize.generate_tokens(io.StringIO(code).readline)
              if t.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT)]
    for i, tok in enumerate(tokens[:-1]):
        if tok.type != tokenize.NAME or tok.string not in GETTEXT_CALLS or tokens[i + 1].string != "(":
            continue
        args, parts, j = [], [], i + 2
        while j < len(tokens) and tokens[j].string != ")":
            if tokens[j].string == ",":
                args.append(parts)
                parts = []
            else:
                parts.append(tokens[j])
            j += 1
        args.append(parts)
        yield tok.string, [_literal(a) for a in args], f"{origin}:{tok.start[0]}"


def marked_strings():
    """Every string the templates and the Python code mark for translation."""
    found = []
    for path in sorted((BASE_DIR / "templates").rglob("*.html")):
        # templatize() turns {% trans "Save" %} into gettext('Save') and blanks out
        # the rest of the template. It keeps the template's indentation, which
        # tokenize would read as Python indentation, so each line is stripped.
        code = templatize(path.read_text(encoding="utf-8"), origin=str(path))
        code = "\n".join(line.strip() for line in code.splitlines())
        found += _gettext_calls(code, path.relative_to(BASE_DIR).as_posix())
    for app in APPS:
        for path in sorted((BASE_DIR / app).rglob("*.py")):
            if "migrations" in path.parts or "tests" in path.parts or path.name == "settings_test.py":
                continue
            found += _gettext_calls(path.read_text(encoding="utf-8"), path.relative_to(BASE_DIR).as_posix())
    return found


def _shown_in(language, function, args):
    """What a visitor reading `language` sees for this gettext call."""
    with translation.override(language):
        if function.startswith("pgettext"):
            return translation.pgettext(args[0], args[1])
        if function.startswith("ngettext"):
            return translation.ngettext(args[0], args[1], 1)
        return translation.gettext(args[0])


def test_scan_finds_strings_in_templates_and_in_code():
    """The scan must see the strings it is meant to check, or the two tests below
    would pass while checking nothing."""
    msgids = {args[0] for _, args, _ in marked_strings() if args and args[0]}

    assert "Proceed to Checkout" in msgids  # a template, {% trans %}
    assert "This product is no longer available." in msgids  # Python, _()
    assert len(msgids) > 250


# Msgids whose Vietnamese text is the same word: brand names, and words Vietnamese
# shoppers use as they are.
SAME_WORD_IN_VIETNAMESE = {"Grocerly", "Email", "Email:", "VNPay", "SKU", "OK", "Tags"}


def test_every_marked_string_has_a_vietnamese_translation():
    """L-47: a string wrapped in {% trans %} or _() but missing from locale/vi
    shows in English on a /vi/ page."""
    missing = []
    for function, args, where in marked_strings():
        msgid = args[1] if function.startswith("pgettext") else args[0]
        if msgid is None or msgid in SAME_WORD_IN_VIETNAMESE:
            continue
        if _shown_in("vi", function, args) == msgid:
            missing.append(f"{where}  {msgid[:70]!r}")

    assert missing == []


def test_marked_strings_are_written_in_english():
    """L-55: the msgid is the English text (CLAUDE.md §7, D-056). A msgid written
    in Vietnamese shows in Vietnamese on /en/ pages."""
    vietnamese = [
        f"{where}  {arg[:60]!r}"
        for _, args, where in marked_strings()
        for arg in args
        if arg and VIETNAMESE.search(arg)
    ]

    assert vietnamese == []


# --- texts the views write in Python ------------------------------------------------

VIEW_MODULES = ["core/views.py", "userauths/views.py", "useradmin/views.py",
                "useradmin/decorators.py", "store_api/views.py"]
# JSON fields whose text the page shows to the visitor.
SHOWN_KEYS = {"message", "error", "reply"}
# Results of a tool call that go to Gemini, not to the visitor; Gemini writes its
# own reply from them (D-035).
FOR_GEMINI_ONLY = {"No matching products found.", "The cart is empty"}


def _is_plain_text(node):
    """A string literal or an f-string: text that never passes through gettext."""
    return isinstance(node, ast.JoinedStr) or (isinstance(node, ast.Constant) and isinstance(node.value, str))


def test_texts_written_by_views_go_through_gettext():
    """L-56: a flash message (`messages.success(request, ...)`) or a JSON field the
    page shows must be a gettext call, not a literal string."""
    literal = []
    for module in VIEW_MODULES:
        tree = ast.parse((BASE_DIR / module).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "messages"
                    and len(node.args) >= 2 and _is_plain_text(node.args[1])):
                literal.append(f"{module}:{node.lineno} messages.{node.func.attr}")
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values, strict=True):
                    if (isinstance(key, ast.Constant) and key.value in SHOWN_KEYS and _is_plain_text(value)
                            and getattr(value, "value", None) not in FOR_GEMINI_ONLY):
                        literal.append(f"{module}:{node.lineno} {key.value!r}")

    assert literal == []


def test_sign_out_message_is_in_the_language_of_the_page(customer_client):
    """L-56: the flash message after signing out follows the page language."""
    page = customer_client.get("/vi/user/sign-out/", follow=True).content.decode()

    assert "You have been logged out successfully." not in page
    assert "Bạn đã đăng xuất." in page


# --- texts that come from Django itself ----------------------------------------------


def test_password_errors_are_all_in_vietnamese():
    """L-57: "123" breaks three password rules; on a /vi/ page all three errors are
    Vietnamese. Django 5 changed the msgid of the too-short error and its vi
    catalog kept the old one, so that error alone showed in English."""
    with translation.override("vi"), pytest.raises(ValidationError) as error:
        validate_password("123")

    assert len(error.value.messages) == 3
    assert all(VIETNAMESE.search(message) for message in error.value.messages)


@pytest.mark.parametrize("check, value", [
    (models.DecimalField().to_python, "abc"),
    (models.IntegerField().to_python, "abc"),
    (validate_image_file_extension, SimpleUploadedFile("notes.txt", b"text")),
])
def test_field_errors_from_django_are_in_vietnamese(check, value):
    """L-57: errors Django writes for a wrong number, or a file that is not an image."""
    with translation.override("vi"), pytest.raises(ValidationError) as error:
        check(value)

    assert VIETNAMESE.search(error.value.messages[0])


# --- pages: the visible text at /vi/ against /en/ -------------------------------------


class VisibleText(HTMLParser):
    """Collect the text of a page a visitor can read: text between tags, plus the
    placeholder and title of boxes. Scripts and styles are skipped."""

    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.texts, self._inside_skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._inside_skip += 1
        for name, value in attrs:
            if name in ("placeholder", "title") and value and value.strip():
                self.texts.append(f"[{name}] {value.strip()}")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._inside_skip:
            self._inside_skip -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if text and not self._inside_skip:
            self.texts.append(text)


def visible_text(html):
    parser = VisibleText()
    parser.feed(html)
    return set(parser.texts)


# A text containing one of these reads the same in both languages and is not a
# translation problem: data the shop typed in (the fixtures' product, supplier and
# customer names, the default storage advice of a product, codes), the language
# switcher, brands and emails.
SAME_IN_BOTH = [
    "Grocerly", "Cà rốt", "Rau củ", "HTX Rau", "Nguyễn Văn", "Võ Văn Ngân", "Tươi ngon",
    "Bảo quản nơi khô ráo", "khachhang", "nhanvien", "@", "Tiếng Việt", "English", "VNPay",
    "Gemini", "INVOICE_NO", "sku",
]
# Whole texts that are the same word in Vietnamese (see SAME_WORD_IN_VIETNAMESE).
SAME_TEXT = {"Email", "Email:", "[placeholder] Email", "cà"}  # "cà": the search query of the page
# Numbers, prices, dates and symbols, or a single letter: nothing to translate.
NO_WORDS = re.compile(r"[\W\d_]*|[\W\d_]*[A-Za-z][\W\d_]*")


def untranslated(client, path):
    """Texts that read the same at /vi<path> and /en<path>."""
    texts = {}
    for language in ("vi", "en"):
        response = client.get(f"/{language}{path}")
        assert response.status_code in (200, 404), f"/{language}{path} answered {response.status_code}"
        texts[language] = visible_text(response.content.decode())
    return sorted(
        text for text in texts["vi"] & texts["en"]
        if not NO_WORDS.fullmatch(text) and text not in SAME_TEXT
        # case-insensitive: a page may print a user name as "Khachhang"
        and not any(name.lower() in text.lower() for name in SAME_IN_BOTH)
    )


@pytest.fixture
def shop(product, vendor, customer):
    """`product` from `vendor`, one review, and two orders of `customer`: one paid
    by COD, one still waiting for its VNPay payment."""
    product.vendor = vendor
    product.save()
    ProductReview.objects.create(user=customer, product=product, review="Tươi ngon", rating=5)
    orders = {}
    for method, paid in (("cod", True), ("online", False)):
        order = CartOrder.objects.create(
            user=customer, price=Decimal("25000.00"), full_name="Nguyễn Văn A", email=customer.email,
            address="1 Võ Văn Ngân, Thủ Đức", payment_method=method, paid_status=paid,
        )
        CartOrderItem.objects.create(
            order=order, invoice_no=f"INVOICE_NO-{order.id}", product=product, item=product.title,
            quantity=1, price=product.price, total=product.price,
        )
        orders[method] = order
    return {"product": product, "vendor": vendor, "cod": orders["cod"].oid, "online": orders["online"].oid}


@pytest.fixture
def staff_client(client, django_user_model, password):
    """The test client, signed in as the store staff (as in useradmin/tests)."""
    staff = django_user_model.objects.create_user(
        email="nhanvien@example.com", username="nhanvien", password=password, is_staff=True
    )
    client.force_login(staff)
    return client


def guest_pages(shop):
    product, vendor = shop["product"], shop["vendor"]
    return [
        "/", "/products/", f"/products/{product.p_id}/", "/categories/",
        f"/categories/{product.category.c_id}/", "/vendors/", f"/vendors/{vendor.v_id}/",
        "/search/?q=c%C3%A0", "/search/?q=", "/cart/", "/contact/", "/about_us/", "/purchase_guide/",
        "/privacy_policy/", "/terms_of_service/", "/coming-soon/", "/user/sign-up/", "/user/sign-in/",
        "/user/password-reset/", "/user/password-reset/done/", "/user/password-reset-confirm/MQ/bad-token/",
        "/user/password-reset-complete/", "/khong-co-trang-nay/",
    ]


def customer_pages(shop):
    return [
        "/dashboard/", f"/dashboard/order/{shop['cod']}/", "/wishlist/", "/checkout-info/",
        f"/checkout/{shop['online']}/", "/user/profile/update/", "/user/change-password/",
        "/user/change-password/done/", f"/payment-completed/{shop['cod']}/", "/payment-failed/",
    ]


def staff_pages(shop):
    return [
        "/useradmin/", "/useradmin/products/", "/useradmin/add-products/",
        f"/useradmin/edit-products/{shop['product'].p_id}/", "/useradmin/orders/",
        f"/useradmin/order_detail/{shop['cod']}/", "/useradmin/shop_page/", "/useradmin/reviews/",
        "/useradmin/settings/", "/useradmin/change_password/",
    ]


def put_in_cart(client, product):
    """The cart and checkout pages send an empty cart back to the home page."""
    client.post(reverse("core:add-to-cart"), {"id": product.id, "qty": 1})


def left_untranslated(client, paths):
    found = {path: untranslated(client, path) for path in paths}
    return {path: texts for path, texts in found.items() if texts}


def test_guest_pages_leave_no_text_untranslated(client, shop):
    """L-55: every page a guest opens reads differently at /vi/ and /en/."""
    put_in_cart(client, shop["product"])

    assert left_untranslated(client, guest_pages(shop)) == {}


def test_customer_pages_leave_no_text_untranslated(customer_client, shop):
    """L-55: every page of a signed-in customer reads differently at /vi/ and /en/."""
    put_in_cart(customer_client, shop["product"])

    assert left_untranslated(customer_client, customer_pages(shop)) == {}


def test_staff_pages_leave_no_text_untranslated(staff_client, shop):
    """L-55: every page of the store staff reads differently at /vi/ and /en/."""
    assert left_untranslated(staff_client, staff_pages(shop)) == {}


def test_comparison_flags_a_text_left_in_one_language():
    """The comparison must flag a text that is the same in both versions, and must
    not flag numbers, prices or names."""
    vi = visible_text("<p>Giỏ hàng</p><p>Free</p><p>25.000 ₫</p><p>Cà rốt Đà Lạt</p><script>x='Free2'</script>")
    en = visible_text("<p>Cart</p><p>Free</p><p>25.000 ₫</p><p>Cà rốt Đà Lạt</p>")

    shared = [t for t in vi & en if not NO_WORDS.fullmatch(t) and not any(n in t for n in SAME_IN_BOTH)]

    assert shared == ["Free"]
    assert "x='Free2'" not in vi


# --- pages: nothing left of the Nest theme --------------------------------------------

THEME_LEFTOVERS = [
    "Nest", "AliThemes", "Evara", "Lorem", "ipsum", "Utah", "Chicago", "Ecommerce Template",
    "E-commerce Dashboard", "Chen Cardigan", "3453012", "(32 reviews)", 'action="#"', "email-protection",
]


def test_pages_hold_no_sample_content_of_the_theme(client, staff_client, shop):
    """L-58: no page shows the theme's sample shop, people, products or Lorem
    ipsum, and no form posts to "#" (a form that only reloads the page)."""
    found = {}
    for browser, paths in ((client, guest_pages(shop)), (staff_client, staff_pages(shop))):
        for path in paths:
            page = browser.get(f"/vi{path}").content.decode()
            hits = [mark for mark in THEME_LEFTOVERS if mark in page]
            if hits:
                found[path] = hits

    assert found == {}
