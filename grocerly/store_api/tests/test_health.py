"""
Health endpoint (/api/v1/health/), polled by the deploy job in CI (P-11, D-036).

No use case covers it: customers never see it. It tells CI which commit the
server is running, so CI knows when a deploy has gone live. Like the rest of
the API it sits outside i18n_patterns, so the path has no /vi/ or /en/ prefix.
"""

from django.urls import reverse


def health_url():
    return reverse("store_api:api-health")


def test_health_reports_the_commit_render_deployed(client, monkeypatch):
    # Render sets RENDER_GIT_COMMIT on every deploy; CI compares it with the
    # commit it has just tested.
    monkeypatch.setenv("RENDER_GIT_COMMIT", "0681855abc")

    response = client.get(health_url())

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "commit": "0681855abc"}


def test_health_reports_unknown_commit_when_not_on_render(client, monkeypatch):
    # Local runs and the test suite have no RENDER_GIT_COMMIT. The answer must
    # never equal a real commit SHA, or CI could take an old server for new.
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)

    response = client.get(health_url())

    assert response.status_code == 200
    assert response.json()["commit"] == "unknown"


def test_health_rejects_post(client):
    response = client.post(health_url())

    assert response.status_code == 405
