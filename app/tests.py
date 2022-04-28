import shutil
from flask_login import login_user
import pytest
import html

from werkzeug.security import generate_password_hash

from .main import (
    AppContextManager,
    get_config,
    update_settings,
    start_model_server,
)


@pytest.fixture(scope="session")
def manager():
    update_settings(get_config("config/test_config.json"))
    from .main import settings

    with AppContextManager(True) as manager:
        if settings.get("doStart"):
            start_model_server()

        manager.app.config.update(
            {
                "TESTING": True,
                "WTF_CSRF_ENABLED": False,
            }
        )
        manager.app.secret_key = "planking at a candlelight vigil"

        yield manager

        # Cleanup
        shutil.rmtree(settings["datadir"], ignore_errors=True)  # Doesn't always exist
        shutil.rmtree(settings["tempdir"], ignore_errors=True)


@pytest.fixture(scope="session")
def client(manager):
    return manager.app.test_client()


@pytest.fixture(scope="session")
def context(manager):
    with manager.app.app_context() as context:
        yield context


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
            },
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
            },
        )

        print(res.data)
        assert res.status_code == 200
        assert b"</ol>" in res.data


def test_del_sample(manager, client):
    from .models import SampleEval

    with manager.app.app_context():
        # First sample must belong to the current user, since no other user
        # could have uploaded any samples
        sample = SampleEval.query.first()
        assert sample is not None

        res = client.get("/eval/new")
        assert res.status_code == 200
        assert str(sample.id) in res.get_data(as_text=True)

        res = client.get(f"/eval/del/{sample.id}", follow_redirects=True)

        print(res.data)
        assert res.status_code == 200
        assert str(sample.id) not in res.get_data(as_text=True)
