from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.models.scholarship import Scholarship


scholarships_bp = Blueprint("scholarships", __name__, url_prefix="/scholarships")


@scholarships_bp.get("/")
@login_required
def index() -> str:
    query = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()

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
