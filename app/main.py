"""
    Thomas: This is the main driver program for the application.
    Most of the actual functionality is delegated to the other modules in this package.
    This module is kind of like a conductor that coordinates them all.
"""

import subprocess
import json
import sys
import secrets
import os
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads

CONF_DIR = "config/"
KEYFILE = os.path.join(CONF_DIR, "key.txt")
CONFIG = os.path.join(CONF_DIR, "config.json")
DB_PATH = "authorid.db"


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
    assert not settings.get("debug") # Will crash

    kill_port_user()    
    subprocess.run("./start_model_server.sh")

    time.sleep(5) # Give tensorflow a few seconds to init


if __name__ == "__main__":
    if settings.get("doStart"):
        start_model_server()

    # Pass "debug" flag in bash to reset the database before and after each run
    flag_debug = settings.get("debug")

    app, db = create_app()
    if flag_debug:
        db.drop_all()

    try:
        os.makedirs(CONF_DIR, exist_ok=True)
        ensure_secret_key(app, KEYFILE)
        db.create_all()

        port = settings.get("port")
        if port is None or not isinstance(port, int):
            app.run(port=8090, debug=flag_debug)
        else:
            app.run(port=port, debug=flag_debug)
    except:
        raise
    finally:
        if flag_debug:
            db.drop_all()

        kill_port_user()
