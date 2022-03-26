"""
    Thomas: This module contains the app views related to user authentication and creation.
    It relies on the flask-login package.
"""

from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, Response, render_template, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user

from .forms import NewUserForm, LoginForm
from .models import db, User


login_manager = LoginManager()
userviews = Blueprint("userviews", __name__, template_folder="templates/")


@login_manager.user_loader
def load_user(user_id: str) -> User:
    return User.query.get(int(user_id))


@userviews.route("/new", methods=["GET", "POST"])
def createuser() -> Response:
    form = NewUserForm()

    if form.validate_on_submit():
        if form.password.data != form.passconf.data:
            form.passconf.errors.append("Passwords don't match!")
            return render_template("users/create.html", form=form)

        userexists = User.query.filter_by(email=form.email.data).one_or_none() is not None
        if userexists:
            form.email.errors.append("Email already registered!")
        else:
            pw_hash = generate_password_hash(form.password.data)
            newuser = User(email=form.email.data, name=form.name.data, pw_hash=pw_hash)
            db.session.add(newuser)
            db.session.commit()

            login_user(newuser, remember=True)
            return redirect(url_for("mainviews.index"))

    # We are either here because the request was a GET or there was an error
    return render_template("users/create.html", form=form)


@userviews.route("/login", methods=["GET", "POST"])
def userlogin() -> Response:
    form = LoginForm()

    if form.validate_on_submit():
        req_user = User.query.filter_by(email=form.email.data).one_or_none()
        if req_user is None:
            form.email.errors.append("Email not registered!")
        else:
            if check_password_hash(req_user.pw_hash, form.password):
                login_user(req_user, remember=True)
                return redirect(url_for("mainviews.index"))
            else:
                form.password.errors.append("Incorrect password!")

    # We are either here because the request was a GET request or login failed.
    return render_template("users/login.html", form=form)


@userviews.route("/logout")
@login_required
def userlogout() -> Response:
    logout_user()
    return redirect(url_for("mainviews.index"))
