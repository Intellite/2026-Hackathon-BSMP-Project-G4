from __future__ import annotations

from app import db


class Scholarship(db.Model):
    __tablename__ = "scholarships"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    award_amount = db.Column(db.Integer, nullable=True)
    eligibility = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.String(50), nullable=True)

    # Prototype fields
    tags = db.Column(db.String(500), nullable=True)  # comma-separated
    created_at = db.Column(db.DateTime, server_default=db.func.now())
