from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.services.ai_service import AIService


roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/roadmap")


@roadmap_bp.get("/")
@login_required
def index() -> str:
    return render_template("dashboard/roadmap.html")


@roadmap_bp.post("/generate")
@login_required
def generate() -> str:
    career_title = request.form.get("career_title", "")
    ai = AIService()
    result = ai.generate_roadmap(
        {
            "career_title": career_title,
            "grade_level": current_user.grade_level,
            "interests": current_user.interests,
            "career_goals": current_user.career_goals,
        }
    )
    return render_template("dashboard/roadmap_result.html", result=result)
