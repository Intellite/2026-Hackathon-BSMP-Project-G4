from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.user import User


profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.get("/")
@login_required
def index() -> str:
    return render_template("profile/index.html", user=current_user)


@profile_bp.post("/update")
@login_required
def update() -> str:
    user: User = current_user  # type: ignore[assignment]

    user.interests = request.form.get("interests", "")
    user.career_goals = request.form.get("career_goals", "")
    user.skills = request.form.get("skills", "")
    user.gpa = float(request.form.get("gpa") or 0) if request.form.get("gpa") else None
    user.activities = request.form.get("activities", "")

    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("profile.index"))
