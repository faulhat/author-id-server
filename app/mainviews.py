"""
    Thomas: This module contains the app views used for the actual app functionality.
    This includes the home page, the file upload forms, and the page for
    displaying model evaluations to the user.
"""

from flask import Blueprint, Response, render_template
from flask_login import current_user


mainviews = Blueprint("mainviews", __name__, template_folder="templates/")


@mainviews.route("/")
def index() -> Response:
    if current_user.is_authenticated:
        return render_template("index.html", user=current_user)
    
    return render_template("index.html")
