"""
    Thomas: This module contains the app views responsible for interaction with the fingerprinting
    model.
"""

import json
import traceback
from typing import BinaryIO
import requests
import numpy as np

from flask import Blueprint, Response, make_response, render_template
from flask_login import current_user, login_required

from .models import UserImage, db, SampleEval
from .forms import LabelledSampleForm, UnlabelledSampleForm
from .main import settings


evalviews = Blueprint("evalviews", __name__, template_folder="templates/")


# Query the model to get a fingerprint for an image
def get_img_fingerprint(image_fp: BinaryIO) -> list[float]:
    query_url = f"http://{settings['modelServerIP']}:{settings['modelServerPort']}/"
    files = {"rq_image": image_fp}
    res = requests.post(query_url, files=files)

    return res.json()


# Add a new labelled image.
@evalviews.route("/new", methods=["GET", "POST"])
@login_required
def new_sample() -> Response:
    form = LabelledSampleForm()
    if form.validate_on_submit():
        try:
            image_fp = form.attachment.data
            fingerprint_json = json.dumps(get_img_fingerprint(image_fp))

            new_image = UserImage(current_user, image_fp)
            db.session.add(new_image)

            new_eval = SampleEval(
                new_image,
                name=form.name.data,
                fingerprint=fingerprint_json,
            )
            db.session.add(new_eval)
            db.session.commit()
        except Exception:
            traceback.print_exc()
            return make_response(
                render_template(
                    "error.html",
                    err_msg="The ID model returned an invalid response! Could not process image.",
                ),
                500,
            )

    user_evals = SampleEval.query.filter_by(user=current_user).order_by(
        SampleEval.timestamp.desc()
    )
    if user_evals.count() == 0:
        return render_template("eval/labelled.html", form=form)

    return render_template("eval/labelled.html", form=form, list_evals=user_evals)


# Get a ranked candidate list for an unlabelled sample
@evalviews.route("/query", methods=["GET", "POST"])
@login_required
def query_model() -> Response:
    form = UnlabelledSampleForm()
    if form.validate_on_submit():
        try:
            image_fp = form.attachment.data
            fingerprint = get_img_fingerprint(image_fp)
            sample_evals = current_user.samples

            distances = []
            for labelled in sample_evals:
                compare_to = json.loads(labelled.fingerprint)
                distances.append(np.linalg.norm(np.asarray(fingerprint) - np.asarray(compare_to)))

            # Get the distances in ascending order while preserving knowledge of indices
            distances = sorted(list(enumerate(distances)), key=lambda t: t[1])

            # Produce a ranked list of labelled samples based on proximity to unlabelled upload
            ranked = [(sample_evals[i], dist) for (i, dist) in distances]
            ranked = [r for (r, _) in ranked]
            return render_template("eval/query.html", form=form, ranked=ranked)
        except Exception:
            traceback.print_exc()
            return make_response(
                render_template(
                    "error.html",
                    err_msg="The ID model returned an invalid response! Could not process image.",
                ),
                500,
            )

    return render_template("eval/query.html", form=form)
