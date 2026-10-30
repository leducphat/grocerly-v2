"""
Errors must reach the Render log although DEBUG is off there (D-038).

Tests run with DEBUG = False, like the KLTN host. On 30/10/2026 the home page
returned 500 there and the log had no traceback, because Django's default
logging prints only while DEBUG is on. These tests point the console handler of
the `django` logger at a buffer and check what a 500 and a 404 print.
"""

import io
import logging

import pytest
from django.test import Client, override_settings
from django.urls import path


def broken_view(request):
    raise RuntimeError("boom from broken_view")


# Used as ROOT_URLCONF by the 500 test, so no real view has to be broken.
urlpatterns = [path("broken/", broken_view)]


@pytest.fixture
def console_output():
    """Send what the `console` handler of the `django` logger prints into a buffer."""
    handler = next(h for h in logging.getLogger("django").handlers if h.name == "console")
    buffer = io.StringIO()
    old_stream = handler.setStream(buffer)
    yield buffer
    handler.setStream(old_stream)


@override_settings(ROOT_URLCONF=__name__)
def test_unhandled_error_prints_traceback_when_debug_is_off(console_output):
    client = Client(raise_request_exception=False)

    response = client.get("/broken/")

    assert response.status_code == 500
    output = console_output.getvalue()
    assert "ERROR django.request: Internal Server Error: /broken/" in output
    assert "Traceback (most recent call last)" in output
    assert "RuntimeError: boom from broken_view" in output


@pytest.mark.django_db
def test_page_not_found_prints_one_line_without_traceback(client, console_output):
    response = client.get("/vi/khong-co-trang-nay/")

    assert response.status_code == 404
    output = console_output.getvalue()
    assert "WARNING django.request: Not Found: /vi/khong-co-trang-nay/" in output
    assert "Traceback" not in output
