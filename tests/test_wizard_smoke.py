"""Smoke test: every wizard step must render without a server error.

Regression guard for the profile-step 500 caused by template code that
referenced `inputs` on steps that don't pass it (July 2026).
"""

import pytest


@pytest.fixture()
def client(flask_app):
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _authenticate(client, with_profile=True):
    with client.session_transaction() as sess:
        sess["authenticated"] = True
        if with_profile:
            sess["profile"] = {
                "email": "smoke@gupshup.io",
                "name": "Smoke Test",
                "country": "India",
                "region": "North",
            }


def test_login_page_renders(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_profile_email_page_renders(client):
    _authenticate(client, with_profile=False)
    resp = client.get("/profile-email")
    assert resp.status_code == 200


@pytest.mark.parametrize("step", ["profile", "volumes", "prices", "results"])
def test_wizard_step_never_500s(client, step):
    """Each step must respond 200 or redirect — never a server error."""
    _authenticate(client)
    resp = client.get(f"/?step={step}")
    assert resp.status_code < 500, (
        f"step={step} returned {resp.status_code} — template or handler error"
    )


def test_profile_step_renders_without_inputs(client):
    """The profile page is rendered without an `inputs` variable; any
    top-level template reference to `inputs` crashes it (the July 2026 bug)."""
    _authenticate(client)
    resp = client.get("/?step=profile")
    assert resp.status_code == 200
    assert b"country" in resp.data.lower()


def test_volumes_step_renders_voice_options(client):
    """Voice channel options must be present on the volumes form."""
    _authenticate(client)
    resp = client.get("/?step=volumes")
    assert resp.status_code == 200
    assert b'value="voice_only"' in resp.data
    assert b'value="text_voice"' in resp.data
