from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.models.scholarship import Scholarship
from app.services.ai_service import AIService

from app.utils.survey_gating import survey_required


scholarships_bp = Blueprint("scholarships", __name__, url_prefix="/scholarships")


@scholarships_bp.get("/")
@login_required
@survey_required
def index() -> str:
    query = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()

    # If AI is configured, generate recommendations tailored to the student.
    # This keeps the prototype demo strong even without a real external scholarships API.
    ai_enabled = bool(current_user.is_authenticated)
    if ai_enabled:
        try:
            ai = AIService()
            ai_result = ai.recommend_scholarships(
                {
                    "student_profile": {
                        "name": current_user.name,
                        "grade_level": current_user.grade_level,
                        "school": current_user.school,
                        "interests": current_user.interests,
                        "career_goals": current_user.career_goals,
                        "skills": current_user.skills,
                        "activities": current_user.activities,
                        "gpa": current_user.gpa,
                    },
                    "filters": {"q": query, "tag": tag},
                }
            )

            recs = ai_result.get("recommendations") if isinstance(ai_result, dict) else None
            if recs and isinstance(recs, list):
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
                    return render_template("scholarships/index.html", results=results)
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

    return render_template("scholarships/index.html", results=results)
