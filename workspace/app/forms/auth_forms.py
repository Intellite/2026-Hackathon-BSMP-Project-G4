from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import FloatField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=255)])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=255)]
    )

    grade_level = StringField("Grade Level", validators=[Optional(), Length(max=50)])
    school = StringField("School", validators=[Optional(), Length(max=120)])

    # For simplicity in prototype: accept comma-separated strings and split in route.
    interests = StringField("Interests (comma-separated)", validators=[Optional(), Length(max=500)])
    career_goals = StringField("Career Goals", validators=[Optional(), Length(max=200)])
    skills = StringField("Skills (comma-separated)", validators=[Optional(), Length(max=500)])
    activities = StringField("Activities (comma-separated)", validators=[Optional(), Length(max=500)])
    gpa = FloatField("GPA", validators=[Optional()])

    submit = SubmitField("Create Account")

    def validate(self, extra_validators=None):  # type: ignore[override]
        # Convert comma-separated fields into lists for convenience.
        if not super().validate(extra_validators=extra_validators):
            return False

        def split_or_empty(value: str | None) -> list[str]:
            if not value:
                return []
            return [x.strip() for x in value.split(",") if x.strip()]

        self.interests.data = split_or_empty(self.interests.data)
        self.skills.data = split_or_empty(self.skills.data)
        self.activities.data = split_or_empty(self.activities.data)
        return True
