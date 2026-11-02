"""
Fixtures for the browser tests (D-042). Run them with `pytest -m e2e`.

`live_server` (pytest-django) starts the real site on the throw-away test database,
and pytest-playwright's `browser` drives a real browser against it. Nothing here
reads grocerly/.env or reaches a real service: the settings are still
grocerly.settings_test.

To use the Chrome that is already installed instead of downloading Chromium, add
`--browser-channel chrome`. CI runs `playwright install chromium` instead.
"""

import os

import pytest
from django.core.servers.basehttp import WSGIServer
from django.test import Client
from django.test.testcases import LiveServerThread

# Playwright's sync API runs an event loop in the test thread, and Django refuses
# database queries made while a loop is running. The tests only create and read
# rows between browser steps, never inside one, so this is safe here.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

OTHER_SITE = "http://other-site.test"


class OneRequestAtATimeServer(WSGIServer):
    """The live server, without a thread per request.

    The test database is SQLite in memory, and Django hands that one connection to
    every thread of the live server. Two requests at once, say an AJAX call and the
    404 of a missing product image, then share it and can read each other's rows:
    on CI the cart came back empty and a wishlist line stayed after a 200. Serving
    requests one by one removes the overlap. Django sends `Connection: close` when
    the server has no threads, so the browser does not wait on an open connection.
    """

    def __init__(self, *args, connections_override=None, **kwargs):
        # Only the threaded server takes this argument; the live server thread
        # already put the shared connection in place before serving.
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def one_request_at_a_time():
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(LiveServerThread, "server_class", OneRequestAtATimeServer)
        yield


@pytest.fixture
def staff(db, django_user_model, password):
    """An account of the store staff: it reaches /useradmin/."""
    return django_user_model.objects.create_user(
        email="nhanvien@example.com", username="nhanvien", password=password, is_staff=True
    )


@pytest.fixture
def sign_in(browser, live_server):
    """Return a function that opens a browser context already signed in as `user`.

    The session cookie is made with Django's test client, so a test does not spend
    its time on the sign-in form; the form has its own tests.
    """
    contexts = []

    def _sign_in(user):
        session = Client()
        session.force_login(user)
        context = browser.new_context()
        context.add_cookies(
            [{"name": "sessionid", "value": session.cookies["sessionid"].value, "url": live_server.url}]
        )
        contexts.append(context)
        return context

    yield _sign_in
    for context in contexts:
        context.close()


@pytest.fixture
def other_site():
    """Return a function that serves `html` at OTHER_SITE in a browser context.

    The host is made up and answered by the browser itself, so Chrome treats it as a
    different site from the shop without a second server.
    """

    def _serve(context, html, path="/"):
        context.route(
            f"{OTHER_SITE}{path}",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html),
        )
        return f"{OTHER_SITE}{path}"

    return _serve
