import pytest
import html

from .main import create_app


# Special sqlite db file just for testing
TEST_DB_PATH = "test.db"


@pytest.fixture()
def app():
    app, db = create_app(TEST_DB_PATH)
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )

    db.drop_all()
    db.create_all()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_field_required(client):
    res = client.post(
        "/users/new",
        data={
            "email": "zarkfrickindinkenberg@facebook.com",
            "name": "",
            "password": "abc",
            "passconf": "abc",
        },
    )

    assert b"Required field" in res.data


def test_email_valid(client):
    res = client.post(
        "/users/new",
        data={
            "email": "asdfads",
            "name": "Rodrigo O!",
            "password": "abc",
            "passconf": "abc",
        },
    )

    assert b"Invalid email" in res.data


def test_password_valid(client):
    res = client.post(
        "/users/new",
        data={
            "email": "amir@daisydinkydailydeals.com",
            "name": "Amir Valerie Blumenfeld",
            "password": "abc",
            "passconf": "123",
        },
    )

    assert "Passwords don't match!" in html.unescape(res.get_data(as_text=True))


def test_user_creation(client):
    res = client.post(
        "/users/new",
        data={
            "email": "anotherday@theraces.com",
            "name": "Amir Hurwitz",
            "password": "abc",
            "password": "abc",
        },
    )

    assert res.status_code == 200
