from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.services.ai_service import AIService


careers_bp = Blueprint("careers", __name__, url_prefix="/careers")


@careers_bp.get("/")
@login_required
def index() -> str:
    return render_template("careers/index.html")


@careers_bp.post("/generate")
@login_required
def generate() -> str:
    interests = request.form.get("interests", "")
    subjects = request.form.get("subjects", "")
    activities = request.form.get("activities", "")
    skills = request.form.get("skills", "")

    ai = AIService()
    result = ai.generate_career_matches(
        {
            "interests": interests,
            "favorite_subjects": subjects,
            "activities": activities,
            "skills": skills,
            "grade_level": current_user.grade_level,
            "career_goals": current_user.career_goals,
        }
    )

    return render_template("careers/results.html", result=result)
