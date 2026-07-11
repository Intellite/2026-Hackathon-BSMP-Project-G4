from __future__ import annotations

from app import db


class Career(db.Model):
    __tablename__ = "careers"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    # Prototype fields
    salary_low = db.Column(db.Integer, nullable=True)
    salary_high = db.Column(db.Integer, nullable=True)
    education = db.Column(db.String(250), nullable=True)
    required_skills = db.Column(db.String(500), nullable=True)  # comma-separated

    created_at = db.Column(db.DateTime, server_default=db.func.now())
