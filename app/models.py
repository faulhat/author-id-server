"""
    Thomas: This module contains the database models, created through the ORM offered
    by the flask-sqlalchemy package.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy_media import Image, ImageAnalyzer, ImageProcessor, ImageValidator

from .main import settings


TEMP_PATH = settings["tempdir"]
db = SQLAlchemy()


class Sample(Image):
    __pre_processors__ = [
        ImageAnalyzer(),
        ImageValidator(
            minimum=(560, 400),
            maximum=(2240, 1600),
            min_aspect_ratio=1.0,
            content_types=['image/jpeg', 'image/png']
        ),
        ImageProcessor(
            fmt='jpeg',
            width=1120,
            height=800,
        )
    ]


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    pw_hash = db.Column(db.String(100), nullable=False)
    evals = db.relationship("SampleEval", back_populates="user")


class SampleEval(db.Model):
    __tablename__ = "sample_eval"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="evals")

    # Name of this handwriting sample's known author
    name = db.Column(db.Text, nullable=False)

    # Image for the sample
    image = db.Column(Sample.as_mutable(db.Json), nullable=False)

    # Fingerprint of the sample
    eval_array = db.Column(db.Json, nullable=False)

