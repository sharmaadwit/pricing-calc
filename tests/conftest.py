import pytest

from app import app


@pytest.fixture(scope="session")
def flask_app():
    """Provide the Flask app object for tests."""
    return app


@pytest.fixture()
def app_ctx(flask_app):
    """Push an application context for tests that need it."""
    with flask_app.app_context():
        yield


@pytest.fixture()
def request_ctx(flask_app):
    """
    Push a full request context (so session is available) for tests
    that call generate_sow_docx or routes directly.
    """
    with flask_app.test_request_context():
        yield


