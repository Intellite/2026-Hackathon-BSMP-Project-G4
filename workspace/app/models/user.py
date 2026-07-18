from __future__ import annotations

from typing import Any

from flask_login import UserMixin
from sqlalchemy import String

from app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(120), unique=True, nullable=False, index=True)
    # Kept for backward compatibility with existing prototype data.
    email = db.Column(String(255), unique=True, nullable=True, index=True)
    password_hash = db.Column(String(255), nullable=False)

    name = db.Column(String(120), nullable=True)
    grade_level = db.Column(String(50), nullable=True)
    school = db.Column(String(120), nullable=True)

    interests = db.Column(String(500), nullable=True)  # comma-separated
    career_goals = db.Column(String(200), nullable=True)

    # Simple profile fields for prototype
    skills = db.Column(String(500), nullable=True)  # comma-separated
    activities = db.Column(String(500), nullable=True)  # comma-separated

    # Scholarship preference tags
    award_amount = db.Column(String(120), nullable=True)
    scholarship_category = db.Column(String(120), nullable=True)
    state = db.Column(String(120), nullable=True)
    other_circumstances = db.Column(String(500), nullable=True)

    # Saved college application cards
    college_applications_json = db.Column(db.Text, nullable=True)

    survey_completed = db.Column(db.Boolean, nullable=False, default=False)

    # Admin authorization (prototype)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self) -> str:  # type: ignore[override]
        return str(self.id)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None
