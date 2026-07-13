from __future__ import annotations

from flask import Blueprint, redirect, render_template, request
from flask_login import login_required

from app.services.college_finder import search_colleges
from app.services.ai_service import AIService
from app.utils.survey_gating import survey_required


college_bp = Blueprint("college", __name__, url_prefix="/college")


@college_bp.get("/")
@login_required
@survey_required
def index() -> str:
    return render_template("dashboard/college_finder.html", results=[])


@college_bp.post("/search")
@login_required
@survey_required
def search() -> str:
    tuition = request.form.get("tuition", "any")
    state = request.form.get("state", "any")
    public_private = request.form.get("public_private", "any")
    major = request.form.get("major", "")

    # Try AI first (parameter-aware). If AI fails/malformed, fall back to demo dataset.
    results = []
    try:
        ai = AIService()
        ai_result = ai.generate_college_matches(
            {
                "filters": {
                    "tuition": tuition,
                    "state": state,
                    "public_private": public_private,
                    "major": major,
                }
            }
        )

        if isinstance(ai_result, dict) and isinstance(ai_result.get("colleges"), list):
            results = ai_result["colleges"][:6]
    except Exception:
        results = []

    if not results:
        results = search_colleges(
            tuition=tuition,
            state=state,
            public_private=public_private,
            major=major,
            limit=6,
        )
    return render_template("dashboard/college_finder.html", results=results)
