"""
The customer's profile page (UC-11, CN-12): /user/profile/update/ shows the
profile of the signed-in customer and saves the changes to that profile only.
Changing the password is Django's own PasswordChangeView and is not tested here.
"""

import pytest
from django.urls import reverse

from userauths.models import Profile

pytestmark = pytest.mark.django_db

PROFILE_URL = "userauths:profile-update"


def new_profile(**changes):
    """What the browser sends when the customer fills in the profile form."""
    data = {
        "full_name": "Trần Thị B",
        "phone": "0912345678",
        "bio": "Thích rau sạch",
        "address": "12 Lê Lợi, Quận 1",
    }
    return {**data, **changes}


@pytest.fixture
def other_customer(django_user_model, password):
    """A second customer, whose profile nobody else may change."""
    user = django_user_model.objects.create_user(
        email="khachkhac@example.com", username="khachkhac", password=password
    )
    Profile.objects.filter(user=user).update(full_name="Lê Văn C", phone="0987654321")
    return user


@pytest.mark.parametrize("method", ["get", "post"])
def test_anonymous_visitor_is_sent_to_sign_in(client, method):
    response = getattr(client, method)(reverse(PROFILE_URL), new_profile())

    assert response.status_code == 302
    assert response.url.startswith(reverse("userauths:sign-in"))
    assert not Profile.objects.filter(full_name="Trần Thị B").exists()


def test_profile_page_shows_the_current_data(customer_client, customer):
    Profile.objects.filter(user=customer).update(full_name="Nguyễn Văn A", phone="0901234567")

    response = customer_client.get(reverse(PROFILE_URL))

    page = response.content.decode()
    assert response.status_code == 200
    assert 'value="Nguyễn Văn A"' in page
    assert 'value="0901234567"' in page


def test_saving_the_profile_updates_it_and_goes_to_the_dashboard(customer_client, customer):
    response = customer_client.post(reverse(PROFILE_URL), new_profile())

    assert response.url == reverse("core:dashboard")
    profile = Profile.objects.get(user=customer)
    assert (profile.full_name, profile.phone, profile.bio, profile.address) == (
        "Trần Thị B", "0912345678", "Thích rau sạch", "12 Lê Lợi, Quận 1",
    )


def test_saving_the_profile_changes_no_other_customer(customer_client, customer, other_customer):
    # The form has no "user" field; a tampered one must not move the profile to someone else.
    customer_client.post(reverse(PROFILE_URL), new_profile(user=other_customer.id))

    other = Profile.objects.get(user=other_customer)
    assert (other.full_name, other.phone) == ("Lê Văn C", "0987654321")
    assert Profile.objects.get(full_name="Trần Thị B").user == customer


def test_rejected_profile_shows_the_error_under_its_box(customer_client, customer, error_under_box):
    too_long = "x" * (Profile._meta.get_field("full_name").max_length + 1)

    response = customer_client.post(reverse(PROFILE_URL), new_profile(full_name=too_long))

    assert response.status_code == 200  # the form again, nothing saved
    assert Profile.objects.get(user=customer).full_name != too_long
    message = response.context["form"].errors["full_name"][0]
    assert error_under_box(response.content.decode(), "full_name", message)
