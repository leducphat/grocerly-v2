"""
The staff profile page /useradmin/settings/ (CN-23: the staff updates their own
profile). SRS.md has no use case for it yet; UC-11 covers the customer's page.
"""

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
