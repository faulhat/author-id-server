"""
    Thomas: This module contains the form objects for the different app views.
    It relies on the flask_wtf package, which is based on Flask and WTForms.
    This delegates any security concerns to that package, which is good because
    it makes my life easier but also because it is typically best practice not to
    implement security yourself and instead rely on libraries.
"""

from wsgiref.validate import validator
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES
from wtforms import EmailField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


images = UploadSet("images", IMAGES)


def default_data_required() -> DataRequired:
    return DataRequired("Required field")


class NewUserForm(FlaskForm):
    email = EmailField(
        "Email address", validators=[default_data_required(), Email("Invalid email")]
    )
    name = StringField("Your name", validators=[default_data_required()])
    password = PasswordField("Password", validators=[default_data_required()])
    passconf = PasswordField("Confirm password", validators=[default_data_required()])
    submit = SubmitField("Create user")


class LoginForm(FlaskForm):
    email = EmailField(
        "User email", validators=[default_data_required(), Email("Invalid email")]
    )
    password = PasswordField("Password", validators=[default_data_required()])
    submit = SubmitField("Log in")


class LabelledSampleForm(FlaskForm):
    name = StringField("Student name", validators=[default_data_required()])
    attachment = FileField(
        "Sample image",
        validators=[
            FileRequired("An image upload is required."),
            FileAllowed(images, "Only image files are allowed."),
        ],
    )

    submit = SubmitField("Upload sample")


class UnlabelledSampleForm(FlaskForm):
    attachment = FileField(
        "Unlabelled image",
        validators=[
            FileRequired("An image upload is required."),
            FileAllowed(images, "Only image files are allowed."),
        ],
    )

    submit = SubmitField("Upload")
