"""
    Thomas: This module contains the database models, created through the ORM offered
    by the flask-sqlalchemy package.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy_imageattach.entity import image_attachment, Image


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    pw_hash = db.Column(db.String(100), nullable=False)
    evals = image_attachment("UserEval")


class UserEval(db.Model, Image):
    __tablename__ = "user_eval"
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    user = db.relationship("User")
    eval_array = db.Column(db.PickleType, nullable=False)

    # Name of this handwriting sample's known author
    name = db.Column(db.Text, nullable=False)
