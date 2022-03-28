"""
    Thomas: This module contains the app views responsible for interaction with the fingerprinting
    model.
"""

import pickle
from typing import BinaryIO
import requests
import numpy as np

from flask import Blueprint, Response, render_template
from flask_login import current_user, login_required

from .models import UserImage, db, SampleEval
from .forms import LabelledSampleForm, UnlabelledSampleForm
from .main import settings


evalviews = Blueprint("evalviews", __name__, template_folder="templates/")


# Query the model to get a fingerprint for an image
def get_img_fingerprint(image_fp: BinaryIO) -> list[float]:
    query_url = settings["modelServerIP"] + ":" + settings["modelServerPort"] + "/eval"
    post_data = {"file": image_fp}
    res = requests.post(query_url, post_data)
    res_data = res.json()

    return res_data


# Add a new labelled image.
@evalviews.route("/new")
@login_required
def new_sample() -> Response:
    form = LabelledSampleForm()

    if form.validate_on_submit():
        image_fp = form.attachment.data
        fingerprint_pkl = pickle.dumps(get_img_fingerprint(image_fp))

        new_image = UserImage(current_user, image_fp, form.attachment.data.filename)
        db.session.add(new_image)

        new_eval = SampleEval(
            image=new_image, name=form.name.data, fingerprint=fingerprint_pkl
        )
        db.session.add(new_eval)
        db.session.commit()

    return render_template("eval/labelled.html", form=form)


# Get a ranked candidate list for an unlabelled sample
@evalviews.route("/query")
@login_required
def query_model() -> Response:
    form = UnlabelledSampleForm()

    if form.validate_on_submit():
        image_fp = form.attachment.data
        fingerprint = get_img_fingerprint(image_fp)
        sample_evals = current_user.evals

        distances = []
        for labelled in sample_evals:
            compare_to = pickle.loads(labelled.fingerprint)
            distances.append(np.linalg.norm(fingerprint - compare_to))

        # Get the distances in ascending order while preserving knowledge of indices
        distances = sorted(list(enumerate(distances)), lambda t: t[1])

        # Produce a ranked list of labelled samples based on proximity to unlabelled upload
        ranked = [(sample_evals[i], dist) for (i, dist) in distances]
        return render_template("eval/query.html", form=form, ranked=ranked)

    return render_template("eval/query.html", ranked=ranked)
