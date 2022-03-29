"""
    Thomas: This is the main driver program for the application.
    Most of the actual functionality is delegated to the other modules in this package.
    This module is kind of like a conductor that coordinates them all.
"""

import json
import sys
import secrets
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads

CONF_DIR = "config/"
KEYFILE = os.path.join(CONF_DIR, "key.txt")
CONFIG = os.path.join(CONF_DIR, "config.json")
DB_PATH = "authorid.db"


# Load configuration
# Provide default settings if no config.json is found
def get_config(config_path: str) -> dict:
    if os.path.exists(config_path):
        with open(config_path, "r") as config:
            return json.load(config)

    return {
        "port": 5001,
        "modelServerPort": 5000,
    }


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


def create_app(db_path: str) -> tuple[Flask, SQLAlchemy]:
    from .userviews import login_manager, userviews
    from .mainviews import mainviews
    from .evaluation import evalviews

    # Initialize database connection
    from .models import db

    # Create and configure Flask object
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
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


# Get settings from config file. This is outside the main block because the settings should
# be globally accessible
settings = get_config(CONFIG)


if __name__ == "__main__":
    # Pass "debug" flag in bash to reset the database before and after each run
    flag_debug = "debug" in sys.argv

    app, db = create_app(DB_PATH)
    if flag_debug:
        db.drop_all()

    try:
        os.makedirs(CONF_DIR, exist_ok=True)
        ensure_secret_key(app, KEYFILE)
        db.create_all()

        port = settings.get("port")
        if port is None or not isinstance(port, int):
            app.run(port=5001, debug=flag_debug)
        else:
            app.run(port=port, debug=flag_debug)
    except:
        if flag_debug:
            db.drop_all()

        raise
