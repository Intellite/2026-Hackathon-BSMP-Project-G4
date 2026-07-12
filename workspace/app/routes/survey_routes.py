from __future__ import annotations

import json
from typing import Any

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.survey import SurveyResponse

survey_bp = Blueprint("survey", __name__, url_prefix="/survey")

# Prototype: one question at a time with fixed options.
SURVEY_QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "goal",
        "prompt": "What is your primary goal for this program?",
        "options": [
            "Explore careers",
            "Build job-ready skills",
            "Prepare for college",
            "Improve my GPA",
            "Get mentorship",
            "Find internships",
            "Strengthen my resume",
            "Learn about scholarships",
            "Develop leadership",
            "Other",
        ],
    },
    {
        "id": "interest_area",
        "prompt": "Which area interests you most?",
        "options": [
            "Healthcare",
            "Technology",
            "Business",
            "Engineering",
            "Education",
            "Skilled trades",
            "Public service",
            "Arts & design",
            "Science",
            "Other",
        ],
    },
    {
        "id": "support_needed",
        "prompt": "What support would help you most right now?",
        "options": [
            "Tutoring",
            "Mentorship",
            "Study plan",
            "Resume help",
            "Interview practice",
            "Scholarship guidance",
            "Time management",
            "Confidence building",
            "Networking",
            "Other",
        ],
    },
    {
        "id": "interests",
        "prompt": "Select your interests (you can choose multiple).",
        "options": [
            "Healthcare",
            "Technology",
            "Business",
            "Engineering",
            "Education",
            "Skilled trades",
            "Public service",
            "Arts & design",
            "Science",
            "Sports & fitness",
            "Law & policy",
            "Environmental work",
            "Music & performance",
            "Photography & media",
            "Robotics",
            "Cybersecurity",
            "Data analytics",
            "Marketing",
            "Entrepreneurship",
            "Other",
        ],
        "multi": True,
    },
    {
        "id": "skills",
        "prompt": "Select your current skills (you can choose multiple).",
        "options": [
            "Communication",
            "Teamwork",
            "Leadership",
            "Problem-solving",
            "Writing",
            "Public speaking",
            "Coding",
            "Math",
            "Science",
            "Design",
            "Research",
            "Organization",
            "Time management",
            "Creativity",
            "Critical thinking",
            "Project planning",
            "Customer service",
            "Technical troubleshooting",
            "Other",
            "None of the above",
        ],
        "multi": True,
    },
    {
        "id": "activities",
        "prompt": "Select activities you enjoy or participate in (you can choose multiple).",
        "options": [
            "Clubs",
            "Sports",
            "Volunteering",
            "Student government",
            "Music",
            "Theater",
            "Art",
            "Robotics/engineering club",
            "Coding club",
            "Debate",
            "Tutoring/mentoring",
            "Internships",
            "Part-time job",
            "Research projects",
            "Community service",
            "Faith/community groups",
            "Family responsibilities",
            "Competitions (science/math/etc.)",
            "Hackathons",
            "Other",
            "None",
        ],
        "multi": True,
    },
    {
        "id": "gpa",
        "prompt": "What is your current GPA?",
        "options": [],
        "type": "gpa",
    },
]


def _get_or_create_response() -> SurveyResponse:
    resp = db.session.execute(
        db.select(SurveyResponse).where(SurveyResponse.user_id == current_user.id)
    ).scalar_one_or_none()
    if resp is None:
        resp = SurveyResponse(user_id=current_user.id, answers_json=json.dumps({}))
        db.session.add(resp)
        db.session.commit()
    return resp


def _load_answers(resp: SurveyResponse) -> dict[str, Any]:
    try:
        return json.loads(resp.answers_json or "{}")
    except Exception:
        return {}


@survey_bp.get("/start")
@login_required
def start() -> str:
    if getattr(current_user, "survey_completed", False):
        return redirect(url_for("dashboard.index"))

    return render_template("survey/start.html")


@survey_bp.get("/step/<int:step>")
@login_required
def step(step: int) -> str:
    if getattr(current_user, "survey_completed", False):
        return redirect(url_for("dashboard.index"))

    if step < 0 or step >= len(SURVEY_QUESTIONS):
        return redirect(url_for("survey.finish"))

    resp = _get_or_create_response()
    answers = _load_answers(resp)

    q = SURVEY_QUESTIONS[step]
    selected = answers.get(q["id"])

    return render_template(
        "survey/step.html",
        question=q,
        step=step,
        total=len(SURVEY_QUESTIONS),
        selected=selected,
    )


@survey_bp.post("/step/<int:step>")
@login_required
def step_post(step: int) -> str:
    if getattr(current_user, "survey_completed", False):
        return redirect(url_for("dashboard.index"))

    if step < 0 or step >= len(SURVEY_QUESTIONS):
        return redirect(url_for("survey.finish"))

    resp = _get_or_create_response()
    answers = _load_answers(resp)

    q = SURVEY_QUESTIONS[step]
    if q.get("type") == "gpa":
        choice = request.form.get("choice", "").strip()
        if not choice:
            flash("Please enter your GPA.", "warning")
            return redirect(url_for("survey.step", step=step))
        answers[q["id"]] = choice
    elif q.get("multi"):
        choices = request.form.getlist("choice_multi")
        if not choices:
            flash("Please select at least one option.", "warning")
            return redirect(url_for("survey.step", step=step))
        # Store as comma-separated string for easy reuse.
        answers[q["id"]] = ",".join(choices)
    else:
        choice = request.form.get("choice")
        if not choice:
            flash("Please select an option.", "warning")
            return redirect(url_for("survey.step", step=step))
        answers[q["id"]] = choice
    resp.answers_json = json.dumps(answers)
    db.session.commit()

    next_step = step + 1
    if next_step >= len(SURVEY_QUESTIONS):
        return redirect(url_for("survey.finish"))
    return redirect(url_for("survey.step", step=next_step))


@survey_bp.get("/finish")
@login_required
def finish() -> str:
    if getattr(current_user, "survey_completed", False):
        return redirect(url_for("dashboard.index"))

    resp = _get_or_create_response()
    resp.completed = True
    db.session.commit()

    # Mark user completed.
    current_user.survey_completed = True
    db.session.commit()

    # Store survey answers into the corresponding profile fields.
    answers = _load_answers(resp)
    if "interests" in answers:
        current_user.interests = answers["interests"]
    if "skills" in answers:
        current_user.skills = answers["skills"]
    if "activities" in answers:
        current_user.activities = answers["activities"]
    if "gpa" in answers:
        try:
            current_user.gpa = float(answers["gpa"])
        except Exception:
            pass
    db.session.commit()

    return render_template("survey/finish.html")


@survey_bp.get("/retake")
@login_required
def retake() -> str:
    # Allow retake only after completion.
    if not getattr(current_user, "survey_completed", False):
        return redirect(url_for("survey.start"))
    return render_template("survey/retake.html")


@survey_bp.post("/retake")
@login_required
def retake_post() -> str:
    if not getattr(current_user, "survey_completed", False):
        return redirect(url_for("survey.start"))

    resp = _get_or_create_response()
    resp.answers_json = json.dumps({})
    resp.completed = False
    db.session.commit()

    current_user.survey_completed = False
    db.session.commit()

    return redirect(url_for("survey.start"))
