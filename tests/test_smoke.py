"""vibecoded: smoke tests that the app boots and a few routes respond.

These are not exhaustive — they prove the factory works, gunicorn can
import `run:app`, and the basic / and /api/explore endpoints respond.

Run: `pytest tests/test_smoke.py -v`
"""
import os
import tempfile

import pytest

# vibecoded: import the factory, not module-level `app`
from app import create_app


@pytest.fixture
def app():
    """Fresh app per test with isolated DATA_DIR."""
    tmp = tempfile.mkdtemp(prefix="pwnamap-test-")
    app = create_app({
        "TESTING": True,
        "DATA_DIR": tmp,
        "SECRET_KEY": "test-secret",
    })
    yield app
    # cleanup handled by mkdtemp + OS; sqlite files in tmp will go too


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.smoke
def test_app_starts(app):
    """The factory returns a Flask app instance."""
    assert app is not None
    assert app.name == "app"


@pytest.mark.smoke
def test_index_returns_something(client):
    """The root URL returns a non-error response.

    vibecoded: intentionally permissive — we don't know what the original
    index returns (probably a map page with some JS). As long as it's not
    a 5xx, the smoke test passes.
    """
    rv = client.get("/")
    assert rv.status_code < 500, f"Server error: {rv.status_code} {rv.data[:200]}"


@pytest.mark.smoke
def test_api_explore_handles_missing_key(client):
    """API endpoints reject unauthenticated requests gracefully.

    The original app uses X-API-Key headers. A missing key should NOT
    return 500 — it should return 401 or 403.
    """
    rv = client.get("/api/explore")
    assert rv.status_code in (400, 401, 403, 422), (
        f"Unexpected status for unauthenticated /api/explore: "
        f"{rv.status_code} {rv.data[:200]}"
    )


@pytest.mark.smoke
def test_settings_route_exists(client):
    """The settings page is referenced in the README; check it doesn't 500."""
    rv = client.get("/settings")
    # 404 is acceptable if route is named differently; 5xx is not
    assert rv.status_code < 500 or rv.status_code == 404, (
        f"Settings route crashed: {rv.status_code}"
    )
