from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models.career import Career
from app.models.scholarship import Scholarship


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("/")
@login_required
def index() -> str:
    careers = Career.query.limit(6).all()
    scholarships = Scholarship.query.limit(6).all()

    # Prototype scoring placeholders
    career_match_score = 78
    skill_gap_summary = [
        {"skill": "Python", "percent": 80},
        {"skill": "Leadership", "percent": 40},
        {"skill": "Internship Experience", "percent": 20},
    ]

    return render_template(
        "dashboard/index.html",
        careers=careers,
        scholarships=scholarships,
        career_match_score=career_match_score,
        skill_gap_summary=skill_gap_summary,
    )
