"""
The staff profile page /useradmin/settings/ (CN-32: the staff updates their own
profile). SRS.md has no use case for it yet; UC-11 covers the customer's page.
"""

import html
import re

import pytest
from django.urls import reverse

from userauths.models import Profile

pytestmark = pytest.mark.django_db

SETTINGS_URL = "useradmin:settings"


def new_profile(**changes):
    """What the browser sends when the staff fills in the settings form."""
    data = {
        "full_name": "Phạm Thị D",
        "phone": "0933111222",
        "bio": "Quản lý kho",
        "address": "1 Võ Văn Ngân, Thủ Đức",
        "country": "Việt Nam",
    }
    return {**data, **changes}


def test_settings_page_shows_the_current_profile(staff_client, staff):
    Profile.objects.filter(user=staff).update(full_name="Phạm Thị D", country="Việt Nam")

    response = staff_client.get(reverse(SETTINGS_URL))

    page = response.content.decode()
    assert response.status_code == 200
    assert 'value="Phạm Thị D"' in page
    assert 'value="Việt Nam"' in page


def test_staff_saves_name_phone_bio_address_and_country(staff_client, staff):
    response = staff_client.post(reverse(SETTINGS_URL), new_profile())

    assert response.url == reverse(SETTINGS_URL)
    profile = Profile.objects.get(user=staff)
    assert (profile.full_name, profile.phone, profile.bio, profile.address, profile.country) == (
        "Phạm Thị D", "0933111222", "Quản lý kho", "1 Võ Văn Ngân, Thủ Đức", "Việt Nam",
    )


def test_saving_without_a_new_photo_keeps_the_old_one(staff_client, staff):
    # The view only replaces the photo when a file was chosen.
    Profile.objects.filter(user=staff).update(image="image/anh-cu.jpg")

    staff_client.post(reverse(SETTINGS_URL), new_profile())

    assert Profile.objects.get(user=staff).image.name == "image/anh-cu.jpg"


def test_customer_cannot_use_the_staff_settings_page(customer_client, customer):
    response = customer_client.post(reverse(SETTINGS_URL), new_profile())

    assert response.url == reverse("userauths:sign-in")
    assert Profile.objects.get(user=customer).full_name is None


def test_anonymous_visitor_cannot_use_the_staff_settings_page(client):
    response = client.post(reverse(SETTINGS_URL), new_profile())

    assert response.url == reverse("userauths:sign-in")
    assert not Profile.objects.filter(full_name="Phạm Thị D").exists()


# ---------- empty boxes (L-45) and too long values (L-50) ----------


def boxes_on_page(page):
    """name -> value of every text box of the page, what the browser sends back on Save."""
    boxes = {}
    for tag in re.findall(r"<input\b[^>]*>", page):
        name = re.search(r'name="([^"]*)"', tag)
        value = re.search(r'value="([^"]*)"', tag)
        if name and 'type="file"' not in tag:
            boxes[name.group(1)] = html.unescape(value.group(1)) if value else ""
    return boxes


@pytest.fixture
def staff_with_empty_boxes(staff):
    Profile.objects.filter(user=staff).update(
        full_name="Phạm Thị D", phone=None, bio=None, address=None, country=None
    )
    return staff


def test_settings_page_shows_empty_boxes_empty(staff_client, staff_with_empty_boxes):
    page = staff_client.get(reverse(SETTINGS_URL)).content.decode()

    assert 'value="None"' not in page


def test_saving_the_page_as_shown_keeps_empty_boxes_empty(staff_client, staff_with_empty_boxes):
    shown = boxes_on_page(staff_client.get(reverse(SETTINGS_URL)).content.decode())

    staff_client.post(reverse(SETTINGS_URL), {**shown, "bio": "Quản lý kho"})

    profile = Profile.objects.get(user=staff_with_empty_boxes)
    assert (profile.full_name, profile.bio) == ("Phạm Thị D", "Quản lý kho")
    assert "None" not in (profile.phone, profile.address, profile.country)


def test_shop_page_does_not_print_none_for_a_missing_address(staff_client, staff_with_empty_boxes):
    page = staff_client.get(reverse("useradmin:shop_page")).content.decode()

    assert not re.search(r"\bNone\b", page)


@pytest.mark.parametrize("field", ["full_name", "phone", "bio", "address", "country"])
def test_too_long_value_never_reaches_the_database(staff_client, staff, field):
    # SQLite stores a string longer than the column, PostgreSQL on the host refuses
    # it and the page answers 500. So the rule is checked here, not the crash.
    limit = Profile._meta.get_field(field).max_length

    staff_client.post(reverse(SETTINGS_URL), new_profile(**{field: "x" * (limit + 1)}))

    assert len(getattr(Profile.objects.get(user=staff), field) or "") <= limit
