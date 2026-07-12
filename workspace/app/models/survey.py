from __future__ import annotations

from app import db


class SurveyResponse(db.Model):
    __tablename__ = "survey_responses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Store survey answers as JSON string for prototype simplicity.
    answers_json = db.Column(db.Text, nullable=False, default="{}")

    completed = db.Column(db.Boolean, nullable=False, default=False)
