from __future__ import annotations

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from app.models.career import Career
from app.models.scholarship import Scholarship




dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("/")
@login_required
def index() -> str:
    careers = Career.query.limit(6).all()
    scholarships = Scholarship.query.limit(6).all()

    # Career match score removed (redundant after first use).
    career_match_score = None
    skill_gap_summary = [
        {"skill": "Python", "percent": 80},
        {"skill": "Leadership", "percent": 40},
        {"skill": "Internship Experience", "percent": 20},
    ]

    # Provide real scholarship entries for the dashboard cards.
    scholarship_cards = []
    for s in scholarships:
        scholarship_cards.append({"scholarship": s, "match_percentage": 60})

    return render_template(
        "dashboard/index.html",
        careers=careers,
        scholarships=scholarship_cards,
        career_match_score=career_match_score,
        skill_gap_summary=skill_gap_summary,
    )
