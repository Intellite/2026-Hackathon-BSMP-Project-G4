from __future__ import annotations

import json
import logging

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.models.scholarship import Scholarship
from app.services.ai_service import AIService

from app.utils.survey_gating import survey_required


scholarships_bp = Blueprint("scholarships", __name__, url_prefix="/scholarships")

logger = logging.getLogger(__name__)


def _persist_dashboard_scholarships(results: list[dict]) -> None:
    """Persist the latest AI scholarship cards for dashboard display."""
    try:
        # Store on the user profile for quick dashboard rendering.
        # If the column doesn't exist yet, this will be ignored.
        if not getattr(current_user, "is_authenticated", False):
            return
        if hasattr(current_user, "dashboard_scholarships_json"):
            current_user.dashboard_scholarships_json = json.dumps(results)
            db.session.commit()
    except Exception:
        # Never break the page if persistence fails.
        pass


@scholarships_bp.get("/")
def index() -> str:
    # Scholarship filters (curated UI on this page only)
    query = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()
    scholarship_type = request.args.get("scholarship_type", "").strip()
    award_amount = request.args.get("award_amount", "").strip()
    state = request.args.get("state", "").strip()
    other_circumstances = request.args.get("other_circumstances", "").strip()

    # Generate recommendations even for anonymous users.
    # If the user is logged in, we enrich the prompt with their profile.
    try:
        ai = AIService()
        ai_result = ai.recommend_scholarships(
            {
                "student_profile": {
                    "name": getattr(current_user, "name", None) if current_user.is_authenticated else None,
                    "grade_level": getattr(current_user, "grade_level", None) if current_user.is_authenticated else None,
                    "school": getattr(current_user, "school", None) if current_user.is_authenticated else None,
                    "interests": getattr(current_user, "interests", None) if current_user.is_authenticated else None,
                    "career_goals": getattr(current_user, "career_goals", None) if current_user.is_authenticated else None,
                    "skills": getattr(current_user, "skills", None) if current_user.is_authenticated else None,
                    "activities": getattr(current_user, "activities", None) if current_user.is_authenticated else None,
                    "gpa": getattr(current_user, "gpa", None) if current_user.is_authenticated else None,
                },
                "filters": {
                    "q": query,
                    "tag": tag,
                    "scholarship_type": scholarship_type,
                    "award_amount": award_amount,
                    "state": state,
                    "other_circumstances": other_circumstances,
                },
            }
        )

        logger.info(
            "AI scholarship raw result type=%s keys=%s",
            type(ai_result).__name__,
            list(ai_result.keys()) if isinstance(ai_result, dict) else None,
        )

        # Strict validation: must be a dict with a list under "recommendations".
        if not isinstance(ai_result, dict):
            raise ValueError("AI result is not a dict")

        recs = ai_result.get("recommendations")
        if not isinstance(recs, list):
            raise ValueError("AI result missing 'recommendations' list")

        if recs:
            results = []
            for r in recs[:12]:
                if not isinstance(r, dict):
                    continue

                name = r.get("name")
                eligibility = r.get("eligibility")
                deadline = r.get("deadline")
                award_amount = r.get("award_amount")
                url = r.get("url")
                match_percentage = r.get("match_percentage")

                # Basic validation to keep cards consistent.
                if not isinstance(name, str) or not name.strip():
                    continue
                if not isinstance(eligibility, str):
                    eligibility = str(eligibility or "")
                if not isinstance(deadline, str):
                    deadline = str(deadline or "")

                try:
                    match_percentage = float(match_percentage)
                except Exception:
                    match_percentage = 0
                match_percentage = max(0, min(100, match_percentage))

                if award_amount is not None:
                    try:
                        award_amount = int(float(award_amount))
                    except Exception:
                        award_amount = None

                results.append(
                    {
                        "scholarship": type(
                            "S",
                            (),
                            {
                                "name": name,
                                "award_amount": award_amount,
                                "url": url if isinstance(url, str) else None,
                                "eligibility": eligibility,
                                "deadline": deadline,
                            },
                        )(),
                        "match_percentage": int(match_percentage),
                    }
                )

            if results:
                _persist_dashboard_scholarships(results[:6])
                return render_template(
                    "scholarships/index.html",
                    results=results,
                    filters={
                        "q": query,
                        "tag": tag,
                        "scholarship_type": scholarship_type,
                        "award_amount": award_amount,
                        "state": state,
                        "other_circumstances": other_circumstances,
                    },
                )
    except Exception:
        # Fall back to DB/prototype data.
        pass

    scholarships = Scholarship.query
    if query:
        scholarships = scholarships.filter(Scholarship.name.ilike(f"%{query}%"))
    if tag:
        scholarships = scholarships.filter(Scholarship.tags.ilike(f"%{tag}%"))

    scholarships = scholarships.limit(20).all()

    # Prototype match percentage
    results = []
    for s in scholarships:
        match = 60
        results.append({"scholarship": s, "match_percentage": match})

    return render_template(
        "scholarships/index.html",
        results=results,
        filters={
            "q": query,
            "tag": tag,
            "scholarship_type": scholarship_type,
            "award_amount": award_amount,
            "state": state,
            "other_circumstances": other_circumstances,
        },
    )
