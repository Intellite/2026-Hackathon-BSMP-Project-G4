from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.services.ai_service import AIService


gap_bp = Blueprint("gap", __name__, url_prefix="/gap")


@gap_bp.get("/")
@login_required
def index() -> str:
    return render_template("dashboard/gap.html")


@gap_bp.post("/analyze")
@login_required
def analyze() -> str:
    target_career = request.form.get("target_career", "")
    ai = AIService()
    result = ai.analyze_skill_gaps(
        {
            "student_profile": {
                "interests": current_user.interests,
                "skills": current_user.skills,
                "activities": current_user.activities,
                "gpa": current_user.gpa,
                "grade_level": current_user.grade_level,
            },
            "target_career": target_career,
        }
    )
    return render_template("dashboard/gap_result.html", result=result)
