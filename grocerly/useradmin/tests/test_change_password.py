"""
The staff change-password page /useradmin/change_password/ (CN-32). SRS.md has no
use case for it; the default is the customer's page (CN-12, UC-11), which uses
Django's PasswordChangeForm (L-51).
"""

import re

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

CHANGE_URL = "useradmin:change_password"
NEW_PASSWORD = "Mat-khau-moi#2026"


def change_password(client, old, new, confirm=None):
    """Post the form the way the staff does.

    Two sets of box names are sent: the ones of the page today (old_password,
    new_password, confirm_new_password) and those of Django's PasswordChangeForm
    (old_password, new_password1, new_password2). The view reads its own set and
    ignores the other, so these tests do not depend on how L-51 is fixed.
    """
    confirm = new if confirm is None else confirm
    data = {
        "old_password": old,
        "new_password": new,
        "confirm_new_password": confirm,
        "new_password1": new,
        "new_password2": confirm,
    }
    return client.post(reverse(CHANGE_URL), data, follow=True)


def test_correct_old_password_changes_the_password(staff_client, staff, password):
    change_password(staff_client, password, NEW_PASSWORD)

    staff.refresh_from_db()
    assert staff.check_password(NEW_PASSWORD)


def test_wrong_old_password_changes_nothing(staff_client, staff, password):
    change_password(staff_client, "sai-mat-khau", NEW_PASSWORD)

    staff.refresh_from_db()
    assert staff.check_password(password)


def test_two_different_new_passwords_change_nothing(staff_client, staff, password):
    change_password(staff_client, password, NEW_PASSWORD, confirm="Mat-khau-khac#2026")

    staff.refresh_from_db()
    assert staff.check_password(password)


def test_customer_cannot_use_the_staff_change_password_page(customer_client, customer, password):
    change_password(customer_client, password, NEW_PASSWORD)

    customer.refresh_from_db()
    assert customer.check_password(password)


def test_password_boxes_hide_what_is_typed(staff_client):
    page = staff_client.get(reverse(CHANGE_URL)).content.decode()

    boxes = [tag for tag in re.findall(r"<input\b[^>]*>", page) if re.search(r'name="[^"]*password[^"]*"', tag)]
    assert len(boxes) == 3
    assert all('type="password"' in tag for tag in boxes)


def test_weak_new_password_is_refused(staff_client, staff, password):
    change_password(staff_client, password, "1")

    staff.refresh_from_db()
    assert staff.check_password(password)


def test_staff_stays_signed_in_after_changing_the_password(staff_client, password):
    response = change_password(staff_client, password, NEW_PASSWORD)

    assert response.wsgi_request.user.is_authenticated
