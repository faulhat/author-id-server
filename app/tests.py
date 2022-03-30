import pytest
import html

from .main import create_app, get_config, update_settings


@pytest.fixture(scope="session")
def app():
    update_settings(get_config("test_config.json"))

    app, db = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    app.secret_key = "it don't matter"

    db.drop_all()
    db.create_all()

    yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


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

    print(res.data)
    assert b"Required field" in res.data


def test_email_valid(client):
    res = client.post(
        "/users/new",
        data={
            "email": "rodrigo",
            "name": "Rodrigo O!",
            "password": "abc",
            "passconf": "abc",
        },
    )

    print(res.data)
    assert b"Invalid email" in res.data


def test_password_valid(client):
    res = client.post(
        "/users/new",
        data={
            "email": "amir@dailydizzydinkydeals.com",
            "name": "Amir Valerie Blumenfeld",
            "password": "abc",
            "passconf": "123",
        },
    )

    print(res.data)
    assert "Passwords don't match!" in html.unescape(res.get_data(as_text=True))


def test_user_creation(client):
    res = client.post(
        "/users/new",
        follow_redirects=True,
        data={
            "email": "anotherday@theraces.com",
            "name": "Amir Hurwitz",
            "password": "abc",
            "passconf": "abc",
        },
    )

    print(res.data)
    assert res.status_code == 200
    assert b"Log out" in res.data


def test_user_logout(client):
    res = client.get("/users/logout", follow_redirects=True)

    print(res.data)
    assert res.status_code == 200
    assert b"Log in" in res.data


def test_user_unregistered(client):
    res = client.post(
        "/users/login",
        data={
            "email": "leeron@poodletartare.info",
            "password": "abc",
        },
    )

    print(res.data)
    assert b"Email not registered" in res.data


def test_wrong_password(client):
    res = client.post(
        "/users/login",
        data={
            "email": "anotherday@theraces.com",
            "password": "jake",
        },
    )

    print(res.data)
    assert b"Incorrect password" in res.data


def test_user_login(client):
    res = client.post(
        "/users/login",
        follow_redirects=True,
        data={
            "email": "anotherday@theraces.com",
            "password": "abc",
        },
    )

    print(res.data)
    assert res.status_code == 200
    assert b"Log out" in res.data


def test_upload_image(client):
    with open("test_data/author1.png", "rb") as image_fp:
        res = client.post(
            "/eval/new",
            data={
                "name": "Doobs",
                "attachment": image_fp,
            }
        )

        print(res.data)
        assert res.status_code == 200
        assert b"</ul>" in res.data


def test_compare_images(client):
    with open("test_data/author2.png", "rb") as image_fp:
        res = client.post(
            "/eval/query",
            data={
                "attachment": image_fp,
            }
        )

        print(res.data)
        assert res.status_code == 200
        assert b"</ol>" in res.data
