"""Security tests for CSRF protection on the prediction form."""
import re

import pytest

from app import app as flask_app


@pytest.fixture
def csrf_client():
    """Flask test client with CSRF protection switched on, as in production."""
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def test_post_without_csrf_token_is_rejected(csrf_client, sample_image_path):
    """A forged POST with no CSRF token is rejected with 400 Bad Request."""
    with open(sample_image_path, "rb") as image_file:
        response = csrf_client.post(
            "/prediction",
            data={"file": (image_file, "sign3.jpeg")},
            content_type="multipart/form-data",
        )
    assert response.status_code == 400


def test_home_page_contains_csrf_token(csrf_client):
    """The upload form includes a hidden csrf_token field."""
    response = csrf_client.get("/")
    assert b'name="csrf_token"' in response.data


def test_post_with_valid_csrf_token_is_accepted(csrf_client, sample_image_path):
    """A real form submission that carries the page's CSRF token is accepted."""
    page = csrf_client.get("/").data.decode()
    token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
    with open(sample_image_path, "rb") as image_file:
        response = csrf_client.post(
            "/prediction",
            data={"csrf_token": token, "file": (image_file, "sign3.jpeg")},
            content_type="multipart/form-data",
        )
    assert response.status_code == 200
    assert b">3<" in response.data
