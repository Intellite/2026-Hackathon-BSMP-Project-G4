from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.utils.survey_gating import survey_required


careers_bp = Blueprint("careers", __name__, url_prefix="/careers")


@careers_bp.get("/")
@login_required
@survey_required
def index() -> str:
    return render_template("careers/index.html")


@careers_bp.post("/generate")
@login_required
@survey_required
def generate() -> str:
    interests = request.form.get("interests", "")
    subjects = request.form.get("subjects", "")
    activities = request.form.get("activities", "")
    skills = request.form.get("skills", "")

    # Career match generation removed (redundant after first use).
    # Keep the endpoint so the UI flow still works.
    result = {
        "careers": [],
        "message": "Career generation is currently disabled. Please use the dashboard and scholarship pages instead."
    }

    return render_template("careers/results.html", result=result)
