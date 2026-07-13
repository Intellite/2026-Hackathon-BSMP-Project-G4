from __future__ import annotations

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from app.models.career import Career
from app.models.scholarship import Scholarship
import json




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

    # Prefer the latest AI-generated scholarship cards (persisted after /scholarships API call).
    scholarship_cards = []
    if getattr(current_user, "is_authenticated", False) and hasattr(current_user, "dashboard_scholarships_json"):
        try:
            raw = getattr(current_user, "dashboard_scholarships_json")
            if raw:
                parsed = json.loads(raw)
                if isinstance(parsed, list) and parsed:
                    scholarship_cards = parsed[:6]
        except Exception:
            scholarship_cards = []

    # Fallback to prototype DB scholarships.
    if not scholarship_cards:
        scholarship_cards = [
            {"scholarship": s, "match_percentage": 60} for s in scholarships[:6]
        ]

    return render_template(
        "dashboard/index.html",
        careers=careers,
        scholarships=scholarship_cards,
        career_match_score=career_match_score,
        skill_gap_summary=skill_gap_summary,
    )
