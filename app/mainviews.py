"""
    Thomas: This module contains the app views used for the actual app functionality.
    This includes the home page, the file upload forms, and the page for
    displaying model evaluations to the user.
"""

from flask import Blueprint, Response, render_template
from flask_login import current_user, login_required

from .models import UserImage


mainviews = Blueprint("mainviews", __name__, template_folder="templates/")


@mainviews.route("/")
def index() -> Response:
    if current_user.is_authenticated:
        return render_template("index.html", user=current_user)

    return render_template("index.html")


@mainviews.route("/image/<int:id>")
@login_required
def get_image(image_id: int) -> Response:
    image = current_user.images.filter_by(UserImage.id == image_id).one_or_none()
    if image is not None:
        with open(image.image_path, "rb") as image_fp:
            return Response(image_fp.read())


@mainviews.route("/image/<int:id>/thumbnail")
@login_required
def get_thumbnail(image_id: int) -> Response:
    image = current_user.images.filter_by(UserImage.id == image_id).one_or_none()
    if image is not None:
        with open(image.thumbnail_path, "rb") as image_fp:
            return Response(image_fp.read())


@mainviews.errorhandler(404)
def not_found():
    return render_template("error.html", err_msg="404! Page not found.")


@mainviews.errorhandler(500)
def internal_error():
    return render_template("error.html", err_msg="500! Server error.")


@mainviews.errorhandler(503)
def access_denied():
    return render_template("error.html", err_msg="503! Could not confirm access to this resource. Are you logged in?")
