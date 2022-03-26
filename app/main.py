import sys
import secrets
import os
import re

from flask import Flask, Response, make_response, session, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

from hashlib import sha256


CONF_DIR = "config/"
KEYFILE = os.path.join(CONF_DIR, "key.txt")
CONFIG = os.path.join(CONF_DIR, "config.json")
DB_PATH = "authorid.db"

# Totally didn't copy this
email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def ensure_secret_key(forApp: Flask, keypath: str) -> None:
    if not os.path.exists(keypath):
        with open(keypath, "w") as keyfile:
            key = secrets.token_hex()
            keyfile.write(key)
            forApp.secret_key = key
    
    with open(keypath, "r") as keyfile:
        forApp.secret_key = keyfile.read()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    pw_hash = db.Column(db.Text, unique=False, nullable=False)
    tokens = db.relationship(
        "UserToken",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __init__(self, email: str, password: str):
        super(db.Model, self).__init__()
        self.email = email
        self.pw_hash = sha256(str(password).encode("utf-8")).hexdigest()


class UserToken(db.Model):
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True)
    user_key = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="tokens")
    data = db.relationship(db.LargeBinary, unique=False, nullable=False)

    def __init__(self, user: User):
        super(db.Model, self).__init__()
        self.user = user
        self.data = bytearray(os.urandom(64))


class Field:
    def __init__(self, name: str, label: str, errors: list[str], mytype: str = "text"):
        self.name = name
        self.label = label
        self.errors = errors
        self.mytype = mytype


@app.route("/createuser", methods=["GET", "POST"])
def createuser() -> Response:
    fields = [
        Field("email", "Email address", []),
        Field("password", "Password", [], mytype="password"),
        Field("passconfirm", "Confirm password", [], mytype="password"),
    ]

    if request.method == "POST":
        err = False

        email = request.form.get("email")
        if email is None or email == "":
            fields[0].errors.append("This field is required!")
            err = True
        elif not re.fullmatch(email_regex, email):
            fields[0].errors.append("Invalid email address!")
            err = True
        
        password = request.form.get("password")
        if password is None or password == "":
            fields[1].errors.append("This field is required!")
            err = True
        
        passconfirm = request.form.get("passconfirm")
        if passconfirm != password:
            fields[2].errors.append("Passwords don't match!")
            err = True

        if err:
            return render_template("createuser.html", fields=fields)

        try:
            newuser = User(email, password)
            db.session.add(newuser)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            fields[0].errors.append("Email already registered!")
            return render_template("createuser.html", fields=fields)
        
        session["user"] = newuser.id

        res = redirect(url_for("usercreated"))
        res.set_cookie()

    return render_template("createuser.html", fields=fields)


@app.route("/usercreated")
def usercreated() -> Response:
    user_id = session.get("user", None)
    if user_id is None:
        return make_response(render_template("usercreated_failure.html"), 500)

    thisuser = User.query.filter(User.id == user_id).first()
    return render_template("usercreated.html", user=thisuser)


@app.route("/login", methods=["GET", "POST"])
def userlogin() -> Response:
    fields = [
        Field("email", "Email", [], "text"),
        Field("password", "Password", [], "password"),
    ]

    if request.method == "POST":
        err = False

        email = request.form.get("email")
        if email is None or email == "":
            fields[0].errors.append("This field is required!")
            err = True
        elif not re.fullmatch(email_regex):
            fields[0].errors.append("Invalid email address!")
            err = True

        password = request.form.get("password")
        if password is None or password == "":
            fields[1].errors.append("This field is required!")
            err = True
        
        if err:
            return render_template("login.html", fields)
    
        queryset = User.query.filter(User.email == email)
        if queryset.count() != 1:
            fields[0].errors.append("Email not registered!")
        else:
            req_user = queryset.first()
            given_pw_hash = sha256(str(password).encode("utf-8")).hexdigest()
            if req_user.pw_hash == given_pw_hash:
                session["user"] = req_user.id
                return redirect(url_for("home"))
            else:
                fields[1].errors.append("Incorrect password!")

    # We are either here because the request was a GET request or login failed.
    return render_template("login.html", fields)


@app.route("/logout")
def userlogout() -> Response:
    del session["user"]

    return redirect(url_for("home"))


if __name__ == "__main__":
    flag_debug = "debug" in sys.argv
    try:
        if flag_debug:
            db.drop_all()

        os.makedirs(CONF_DIR, exist_ok=True)

        ensure_secret_key(app, KEYFILE)

        db.create_all()
        app.run(debug=flag_debug)
    except:
        if flag_debug:
            db.drop_all()