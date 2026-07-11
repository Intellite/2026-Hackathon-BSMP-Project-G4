from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user, login_required

from app.services.ai_service import AIService


resume_bp = Blueprint("resume", __name__, url_prefix="/resume")


@resume_bp.get("/")
@login_required
def index() -> str:
    return render_template("dashboard/resume_analyzer.html")


@resume_bp.post("/analyze")
@login_required
def analyze() -> str:
    file = request.files.get("resume")
    if not file or not file.filename:
        flash("Please upload a resume file.", "warning")
        return redirect("resume.index")

    content = file.read().decode("utf-8", errors="ignore")
    ai = AIService()
    result = ai.analyze_resume({"resume_text": content, "student_profile": current_user.name})

    return render_template("dashboard/resume_result.html", result=result)
