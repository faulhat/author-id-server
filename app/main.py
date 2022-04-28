"""
    Thomas: This is the main driver program for the application.
    Most of the actual functionality is delegated to the other modules in this package.
    This module is kind of like a conductor that coordinates them all.
"""

import subprocess
import json
import secrets
import os
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash

CONF_DIR = "config/"
KEYFILE = os.path.join(CONF_DIR, "key.txt")
CONFIG = os.path.join(CONF_DIR, "config.json")
DB_PATH = "authorid.db"

TEST_USER_EMAIL = "user@test.com"
TEST_USER_PW = "login"


# Load configuration
def get_config(config_path: str) -> dict:
    with open(config_path, "r") as config:
        return json.load(config)


# Ensure that there is a viable secret key for the app to use for session encryption
def ensure_secret_key(forApp: Flask, keypath: str) -> None:
    if not os.path.exists(keypath):
        # If there currently is no key file, create one with a new securely generated key
        with open(keypath, "w") as keyfile:
            key = secrets.token_hex()
            keyfile.write(key)
            forApp.secret_key = key
    else:
        # Otherwise, load the existing key
        with open(keypath, "r") as keyfile:
            forApp.secret_key = keyfile.read()


# Get settings from config file. This is outside the main block because the settings should
# be globally accessible
settings = get_config(CONFIG)


def create_app() -> tuple[Flask, SQLAlchemy]:
    from .userviews import login_manager, userviews
    from .mainviews import mainviews
    from .evaluation import evalviews

    # Initialize database connection
    from .models import db

    # Create and configure Flask object
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings["db_uri"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database mediator objects
    db.init_app(app)
    login_manager.init_app(app)

    # Incorporate the userviews and mainviews modules
    app.register_blueprint(userviews, url_prefix="/users")
    app.register_blueprint(mainviews)
    app.register_blueprint(evalviews, url_prefix="/eval")
    app.app_context().push()

    return app, db


# Replace settings with new settings. For use by other modules.
def update_settings(new_conf: dict) -> None:
    global settings
    settings = new_conf


# Kill process using port required
def kill_port_user():
    subprocess.run(["fuser", f"{settings.get('modelServerPort')}/tcp", "--kill"])


# Start model server here
def start_model_server():
    assert not settings.get("debug")  # Will crash

    kill_port_user()
    subprocess.run("./start_model_server.sh")

    time.sleep(5)  # Give tensorflow a few seconds to init


class AppContextManager:
    """
        This context manager guarantees proper initialization and finalization
        of the app state. This way, no messy try-finally block is necessary in the main block
    """

    def __init__(self, flag_debug):
        self.flag_debug = flag_debug
        self.app, self.db = create_app()

    def __enter__(self):
        if self.flag_debug:
            self.db.drop_all()

        return self
    
    def __exit__(self, *_):
        if self.flag_debug:
            self.db.drop_all()

        kill_port_user()


if __name__ == "__main__":
    from .models import User

    if settings.get("doStart"):
        start_model_server()

    # Set debug to true in config to clear the database before and after each run.
    # You can also change the database URI in the config, so you can have multiple databases
    # (e.g. one for testing and one for deployment)
    flag_debug = settings.get("debug")
    with AppContextManager(flag_debug) as manager:
        os.makedirs(CONF_DIR, exist_ok=True)
        ensure_secret_key(manager.app, KEYFILE)
        manager.db.create_all()

        if settings.get("test_user"):
            test_user_email = settings.get("test_user_email", TEST_USER_EMAIL)
            test_user_pw = settings.get("test_user_pw", TEST_USER_PW)

            test_user = User.query.filter_by(email=test_user_email).one_or_none()
            if test_user is not None:
                manager.db.session.delete(test_user)
                manager.db.session.commit()

            pw_hash = generate_password_hash(test_user_pw)
            test_user = User(email=test_user_email, name="Test User", pw_hash=pw_hash)
            manager.db.session.add(test_user)
            manager.db.session.commit()

            print(f"Test user email: {test_user_email}")
            print(f"Test user password: {test_user_pw}")

        port = settings.get("port")
        if port is None or not isinstance(port, int):
            manager.app.run(port=8090, debug=flag_debug)
        else:
            manager.app.run(port=port, debug=flag_debug)
