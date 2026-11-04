"""
Which email backend sends the shop's mail (L-43, D-050).

The only mail Grocerly sends is the password reset link (CN-03). The host runs
on Render's free plan, which blocks SMTP ports, so real mail goes out through
Brevo's HTTPS API with the django-anymail backend. A work machine or the test
suite without a Brevo key prints the mail to the console instead, so nothing is
sent by accident.
"""

BREVO_BACKEND = "anymail.backends.brevo.EmailBackend"
CONSOLE_BACKEND = "django.core.mail.backends.console.EmailBackend"


def pick_email_backend(brevo_api_key: str) -> str:
    """Brevo when a key is set, the console otherwise."""
    if brevo_api_key:
        return BREVO_BACKEND
    return CONSOLE_BACKEND
