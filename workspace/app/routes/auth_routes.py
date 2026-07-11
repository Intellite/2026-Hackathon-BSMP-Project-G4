from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.user import User

from app.forms.auth_forms import LoginForm, SignupForm


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    return render_template("auth/login.html", form=form)


@auth_bp.post("/login")
def login_post() -> str:
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("auth/login.html", form=form)

    user = db.session.execute(
        db.select(User).where(User.email == form.email.data)
    ).scalar_one_or_none()

    if user is None or not check_password_hash(user.password_hash, form.password.data):
        flash("Invalid email or password.", "danger")
        return render_template("auth/login.html", form=form)

    login_user(user)
    return redirect(url_for("dashboard.index"))


@auth_bp.get("/signup")
def signup() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = SignupForm()
    return render_template("auth/signup.html", form=form)


@auth_bp.post("/signup")
def signup_post() -> str:
    form = SignupForm()
    if not form.validate_on_submit():
        return render_template("auth/signup.html", form=form)

    existing = db.session.execute(
        db.select(User).where(User.email == form.email.data)
    ).scalar_one_or_none()
    if existing is not None:
        flash("Email already registered.", "warning")
        return render_template("auth/signup.html", form=form)

    user = User(
        email=form.email.data,
        password_hash=generate_password_hash(form.password.data),
        name=form.name.data,
        grade_level=form.grade_level.data,
        school=form.school.data,
        interests=",".join(form.interests.data) if form.interests.data else "",
        career_goals=form.career_goals.data,
        skills=",".join(form.skills.data) if form.skills.data else "",
        activities=",".join(form.activities.data) if form.activities.data else "",
        gpa=form.gpa.data,
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for("dashboard.index"))


@auth_bp.post("/logout")
@login_required
def logout() -> str:
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home.home"))
