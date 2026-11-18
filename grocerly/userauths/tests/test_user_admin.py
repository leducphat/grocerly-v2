"""
Making a customer staff in the Django admin (UC-22, CN-25).

SRS §6.1: a staff account is made by the person signing up as a customer, then the
admin ticks is_staff in the admin. Sign-up never asks for a bio, but User.bio has no
blank=True, so the admin change form refuses to save until the admin types one
(L-80, seen on the host on 18/11/2026).
"""

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user_form(django_user_model, password):
    """The form class the admin change page of a user is built from."""
    superuser = django_user_model.objects.create_superuser(
        email="quantri@example.com", username="quantri", password=password
    )
    request = RequestFactory().get("/")
    request.user = superuser
    return admin.site._registry[get_user_model()].get_form(request)


@pytest.mark.xfail(reason="L-80: User.bio has no blank=True, so the admin form requires it")
def test_admin_user_form_does_not_require_a_bio(admin_user_form, customer):
    assert customer.bio == ""  # sign-up leaves it empty

    form = admin_user_form(instance=customer)

    assert form.fields["bio"].required is False
