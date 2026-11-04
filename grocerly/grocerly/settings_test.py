"""
Settings for the automated test suite (pytest). See docs/DECISIONS.md D-018.

settings.py copies every key of grocerly/.env into os.environ, and that .env may
still point at the TLCN production database, Cloudinary account and Gemini key
(D-002). Environment variables therefore cannot switch tests to a safe setup, so
this module imports the normal settings and then overrides everything that
talks to the outside world.
"""

import os

from .settings import *  # noqa: F401,F403

SECRET_KEY = "test-only-secret-key-not-used-anywhere-else"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Never the database from .env: a private in-memory SQLite database that
# pytest-django creates and throws away on every run.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Uploaded files stay in memory instead of going to Cloudinary or media/.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# A weak but fast hasher: tests create many users, real hashing is slow on purpose.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# VNPay: a made-up merchant and secret. Tests sign payment responses with this
# secret themselves; no request ever reaches VNPay.
VNPAY_TMN_CODE = "TESTTMN"
VNPAY_HASH_SECRET = "test-vnpay-hash-secret"
VNPAY_PAYMENT_URL = "https://vnpay.test/paymentv2/vpcpay.html"
VNPAY_API_URL = ""

# Mail never reaches Brevo (L-43): the key copied from .env is dropped, and
# pytest-django collects sent mail in an in-memory outbox. Tests of the Brevo
# backend set a fake key and fake Brevo's answer themselves (userauths/tests).
BREVO_API_KEY = ""
ANYMAIL = {"BREVO_API_KEY": "", "REQUESTS_TIMEOUT": 10}
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "Grocerly <shop@example.com>"

# store_api/views.py reads GEMINI_API_KEY when it is first imported. Blanking it
# here means a test can never send a message to the real Gemini API; tests that
# need the assistant replace the model with a fake (store_api/tests).
os.environ["GEMINI_API_KEY"] = ""
