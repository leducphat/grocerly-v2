"""
Account tests: sign up (UC-01), sign in (UC-02), sign out (UC-10), and the staff
routing rule of RestrictStaffMiddleware (CLAUDE.md section 7).

Automates the manual cases TC_01-TC_04 of docs/SRS.md section 7.
"""

import pytest
from django.urls import reverse

from userauths.models import Profile, User

pytestmark = pytest.mark.django_db


def is_signed_in(client):
    return "_auth_user_id" in client.session


def sign_up_data(email, password, password2=None):
    return {
        "email": email,
        "username": "khachmoi",
        "password1": password,
        "password2": password if password2 is None else password2,
    }


# ---------- UC-01: sign up ----------


def test_sign_up_with_valid_data_creates_account_and_signs_in(client, password):
    # TC_03
    response = client.post(reverse("userauths:sign-up"), sign_up_data("moi@example.com", password))

    assert response.status_code == 302
    assert response.url == reverse("core:index")
    assert User.objects.filter(email="moi@example.com").exists()
    assert is_signed_in(client)


def test_sign_up_with_email_already_used_is_rejected(client, customer, password):
    # TC_04
    response = client.post(reverse("userauths:sign-up"), sign_up_data(customer.email, password))

    assert response.status_code == 200  # the form is shown again with an error
    assert User.objects.filter(email=customer.email).count() == 1
    assert not is_signed_in(client)


def test_sign_up_with_different_passwords_creates_no_account(client, password):
    response = client.post(
        reverse("userauths:sign-up"), sign_up_data("moi@example.com", password, password + "x")
    )

    assert response.status_code == 200
    assert not User.objects.filter(email="moi@example.com").exists()


def test_sign_up_with_weak_password_creates_no_account(client):
    response = client.post(reverse("userauths:sign-up"), sign_up_data("moi@example.com", "12345678"))

    assert response.status_code == 200
    assert not User.objects.filter(email="moi@example.com").exists()


def test_new_account_gets_a_profile(django_user_model, password):
    # The profile page (UC-11) loads Profile.objects.get(user=...) and would crash without it.
    user = django_user_model.objects.create_user(email="moi@example.com", username="moi", password=password)

    assert Profile.objects.filter(user=user).exists()


# ---------- UC-02: sign in ----------


def test_sign_in_with_correct_email_and_password_signs_in(client, customer, password):
    # TC_01
    response = client.post(reverse("userauths:sign-in"), {"email": customer.email, "password": password})

    assert response.status_code == 302
    assert response.url == reverse("core:index")
    assert int(client.session["_auth_user_id"]) == customer.pk


def test_sign_in_with_wrong_password_does_not_sign_in(client, customer):
    # TC_02
    response = client.post(reverse("userauths:sign-in"), {"email": customer.email, "password": "sai-mat-khau"})

    assert response.status_code == 200
    assert not is_signed_in(client)


def test_sign_in_with_unknown_email_does_not_sign_in(client, password):
    response = client.post(reverse("userauths:sign-in"), {"email": "khongco@example.com", "password": password})

    assert response.status_code == 200
    assert not is_signed_in(client)


def test_staff_sign_in_goes_to_store_dashboard(client, django_user_model, password):
    staff = django_user_model.objects.create_user(
        email="nhanvien@example.com", username="nhanvien", password=password, is_staff=True
    )

    response = client.post(reverse("userauths:sign-in"), {"email": staff.email, "password": password})

    assert response.url == reverse("useradmin:dashboard")


def test_superuser_sign_in_goes_to_django_admin(client, django_user_model, password):
    admin = django_user_model.objects.create_superuser(
        email="quantri@example.com", username="quantri", password=password
    )

    response = client.post(reverse("userauths:sign-in"), {"email": admin.email, "password": password})

    assert response.url == "/admin/"


# ---------- UC-10: sign out ----------


def test_sign_out_ends_session_and_returns_to_sign_in(customer_client):
    response = customer_client.get(reverse("userauths:sign-out"))

    assert response.url == reverse("userauths:sign-in")
    assert not is_signed_in(customer_client)


# ---------- Staff routing (RestrictStaffMiddleware) ----------


def test_staff_opening_the_storefront_is_sent_to_store_dashboard(client, django_user_model, password):
    staff = django_user_model.objects.create_user(
        email="nhanvien@example.com", username="nhanvien", password=password, is_staff=True
    )
    client.force_login(staff)

    response = client.get(reverse("core:cart"))

    assert response.status_code == 302
    assert response.url == reverse("useradmin:dashboard")
