from checker import create_app
import pytest

@pytest.fixture(scope="module")
def test_client():
    config = {"TESTING": True, "WTF_CSRF_ENABLED": False}
    app = create_app(config)
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()
