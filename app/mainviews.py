"""
    Thomas: This module contains the app views used for the actual app functionality.
    This includes the home page, the file upload forms, and the page for
    displaying model evaluations to the user.
"""

from flask import Blueprint, Response, render_template, abort
from flask_login import current_user, login_required

from .models import UserImage


mainviews = Blueprint("mainviews", __name__, template_folder="templates/")


@mainviews.route("/")
def index() -> Response:
    if current_user.is_authenticated:
        return render_template("index.html", user=current_user)

    return render_template("index.html")


@mainviews.route("/image/<int:image_id>")
@login_required
def get_image(image_id: int) -> Response:
    image = (
        UserImage.query.filter_by(id=image_id)
        .filter_by(user=current_user)
        .one_or_none()
    )
    if image is not None:
        with open(image.image_path, "rb") as image_fp:
            return Response(image_fp.read(), mimetype="image")

    abort(404)


@mainviews.route("/image/<int:image_id>/thumbnail")
@login_required
def get_thumbnail(image_id: int) -> Response:
    image = (
        UserImage.query.filter_by(id=image_id)
        .filter_by(user=current_user)
        .one_or_none()
    )
    if image is not None:
        with open(image.thumbnail_path, "rb") as image_fp:
            return Response(image_fp.read(), mimetype="image")

    abort(404)


@mainviews.app_errorhandler(404)
def not_found(_):
    return render_template("error.html", err_msg="404! Page not found."), 404


@mainviews.app_errorhandler(500)
def internal_error(_):
    return render_template("error.html", err_msg="500! Server error."), 500


@mainviews.app_errorhandler(401)
def access_denied(_):
    return (
        render_template(
            "error.html",
            err_msg="401! Could not confirm access to this resource. Are you logged in?",
        ),
        401,
    )
