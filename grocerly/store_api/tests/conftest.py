import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def forget_failed_gemini_models():
    """The assistant remembers a failed Gemini model in Django's cache (D-060).
    The cache lives in memory for the whole test run, so clear it around each test."""
    cache.clear()
    yield
    cache.clear()
