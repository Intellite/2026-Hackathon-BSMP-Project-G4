from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.utils.survey_gating import survey_required
from app.services.ai_service import AIService


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

    ai = AIService()
    result = ai.generate_career_matches(
        {
            "interests": interests,
            "subjects": subjects,
            "activities": activities,
            "skills": skills,
            "student_profile": current_user.name,
            "grade_level": current_user.grade_level,
        }
    )

    return render_template("careers/results.html", result=result)


@careers_bp.get("/results")
@login_required
@survey_required
def results() -> str:
    # Simple fallback so the UI can navigate directly to /careers/results.
    result = {
        "careers": [],
        "message": "No results yet. Submit the form on the Career Explorer page to generate recommendations."
    }
    return render_template("careers/results.html", result=result)
