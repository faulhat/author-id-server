from re import template
from flask import Blueprint, Response

from .forms import LabelledSampleForm, UnlabelledSampleForm
from .main import settings


evalviews = Blueprint("evalviews", __name__, template_folder="templates/")


# Add a new labelled image.
@evalviews.route("/new")
def new_sample():
    form = LabelledSampleForm()

    if form.validate_on_submit():
        pass
