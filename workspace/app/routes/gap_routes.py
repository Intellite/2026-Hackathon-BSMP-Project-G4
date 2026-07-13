from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, session
from flask_login import current_user, login_required

from app.services.ai_service import AIService

from app.utils.survey_gating import survey_required


gap_bp = Blueprint("gap", __name__, url_prefix="/gap")


@gap_bp.get("/")
@login_required
@survey_required
def index() -> str:
    return render_template("dashboard/gap.html")


@gap_bp.post("/analyze")
@login_required
@survey_required
def analyze() -> str:
    target_career = request.form.get("target_career", "")
    ai = AIService()
    result = ai.analyze_skill_gaps(
        {
            "student_profile": {
                "interests": current_user.interests,
                "skills": current_user.skills,
                "activities": current_user.activities,
                "gpa": getattr(current_user, "gpa", None),
                "grade_level": current_user.grade_level,
            },
            "target_career": target_career,
        }
    )

    # Persist top 3 gaps for dashboard auto-fill.
    try:
        gaps = result.get("gaps") if isinstance(result, dict) else None
        if isinstance(gaps, list) and gaps:
            top3 = gaps[:3]
            session["last_gap_top3"] = [
                {
                    "name": g.get("name"),
                    "current_percent": g.get("current_percent"),
                }
                for g in top3
                if isinstance(g, dict)
            ]
    except Exception:
        session.pop("last_gap_top3", None)

    return render_template("dashboard/gap_result.html", result=result)


@gap_bp.get("/top3")
@login_required
def top3():
    top3 = session.get("last_gap_top3")
    if not top3:
        return jsonify({"top3": []})
    return jsonify({"top3": top3})
