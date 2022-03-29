"""
    Thomas: This module contains the database models, created through the ORM offered
    by the flask-sqlalchemy package.
"""

import hashlib
import os
from typing import BinaryIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from PIL import Image

from .main import settings


TEMP_PATH = settings["tempdir"]
DATA_PATH = os.path.join("app/", "data/")
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    pw_hash = db.Column(db.String(100), nullable=False)
    images = db.relationship(
        "UserImage", back_populates="user", cascade="all, delete-orphan"
    )
    samples = db.relationship(
        "SampleEval", back_populates="user", cascade="all, delete-orphan"
    )


class UserImage(db.Model):
    __tablename__ = "image"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="images")

    # Image for the sample as filename
    image_path = db.Column(db.Text, nullable=False)
    thumbnail_path = db.Column(db.Text, nullable=False)

    sample = db.relationship("SampleEval", back_populates="image", uselist=False)

    def __init__(self, user: User, image_fp: BinaryIO, filename: str):
        super(db.Model, self).__init__()
        self.user = user
        directory = os.path.join(DATA_PATH, str(user.id))
        os.makedirs(directory)

        # Generate a path unique enough that collisions are impossible
        digest = hashlib.sha1(image_fp.read()).hexdigest()
        new_filename = f"{filename}-{digest[:10]}"
        self.image_path = os.path.join(directory, new_filename)
        with open(self.image_path, "wb") as store_to:
            store_to.write(image_fp.read())

        self.thumbnail_path = new_filename + "thumbnail.png"
        with Image.open(image_fp) as image:
            factor: float
            if image.size[0] > image.size[1]:
                factor = 100 / image.size[0]
            else:
                factor = 100 / image.size[1]

            thumbnail = image.resize(
                (int(factor * image.size[0]), int(factor * image.size[1]))
            )
            with open(self.thumbnail_path, "wb") as store_to:
                thumbnail.save(store_to)


class SampleEval(db.Model):
    __tablename__ = "sample"

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("image.id"))
    image = db.relationship("UserImage", back_populates="sample")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="samples")

    # Name of this handwriting sample's known author
    name = db.Column(db.Text, nullable=False)

    # Fingerprint of the sample
    fingerprint = db.Column(db.Text, nullable=False)

    def __init__(self, image: UserImage, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image = image
        self.user = image.user
