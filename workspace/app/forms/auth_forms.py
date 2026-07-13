from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=255)])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=255)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), Length(min=6, max=255)]
    )

    grade_level = SelectField(
        "Grade Level",
        choices=[
            ("6th Grade", "6th Grade"),
            ("7th Grade", "7th Grade"),
            ("8th Grade", "8th Grade"),
            ("9th Grade", "9th Grade"),
            ("10th Grade", "10th Grade"),
            ("11th Grade", "11th Grade"),
            ("12th Grade", "12th Grade"),
            ("College Freshman", "College Freshman"),
            ("College Sophomore", "College Sophomore"),
            ("College Junior", "College Junior"),
            ("College Senior", "College Senior"),
        ],
        validators=[DataRequired()],
    )

    submit = SubmitField("Create Account")

    def validate(self, extra_validators=None):  # type: ignore[override]
        # Convert comma-separated fields into lists for convenience.
        if not super().validate(extra_validators=extra_validators):
            return False

        if self.password.data != self.confirm_password.data:
            self.confirm_password.errors.append("Passwords do not match.")
            return False

        return True
