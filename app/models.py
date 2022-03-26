"""
    Thomas: This module contains the database models, created through the ORM offered
    by the flask-sqlalchemy package.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, unique=False, nullable=False)
    pw_hash = db.Column(db.String(100), unique=False, nullable=False)
