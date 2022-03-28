"""
    Thomas: This module contains the app views responsible for interaction with the fingerprinting
    model.
"""

import requests

from flask import Blueprint, Response
from flask_login import login_required

from .models import UserEval
from .forms import LabelledSampleForm, UnlabelledSampleForm
from .main import settings


evalviews = Blueprint("evalviews", __name__, template_folder="templates/")


# Add a new labelled image.
@evalviews.route("/new")
@login_required
def new_sample() -> Response:
    form = LabelledSampleForm()

    if form.validate_on_submit():
        query_url = settings["modelServerIP"] + ":" + \
            settings["modelServerPort"] + "/eval"
        post_data = {"file": form.attachment.data}
        res = requests.post(query_url, post_data)
        res_data = res.json()

        new_eval = UserEval(name=form.name.data, attachment=form.attachment.data)

