"""
Thumbnails that the Django admin shows for order items (D-029).

Ruff rule S308 flagged the mark_safe calls that built these <img> tags. The
order item one mattered most: its `image` is a plain string stored with the
order, and before D-022 that string came from the browser.
"""

from core.models import CartOrderItem


def test_order_item_image_escapes_the_stored_value():
    item = CartOrderItem(image='x.jpg" onerror="alert(1)')

    html = item.order_image()

    assert 'onerror="alert(1)"' not in html
    assert "&quot;" in html


def test_order_item_image_uses_the_stored_url_as_it_is():
    """The stored value is already product.image.url, so no /media/ prefix."""
    item = CartOrderItem(image="/media/products/carrot.jpg")

    html = item.order_image()

    assert 'src="/media/products/carrot.jpg"' in html
