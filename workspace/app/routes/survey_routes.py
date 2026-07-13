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
        "id": "award_amount",
        "prompt": "What award amount are you aiming for?",
        "options": [
            "Under $1,000",
            "$1,000–$4,999",
            "$5,000–$9,999",
            "$10,000–$24,999",
            "$25,000+",
            "Not sure yet",
        ],
    },
    {
        "id": "scholarship_category",
        "prompt": "What type of scholarship are you most interested in?",
        "options": [
            "Merit-based",
            "Need-based",
            "Competition-based",
            "STEM/major-specific",
            "Community/service",
            "First-generation",
            "Athletics",
            "Career/industry program",
            "Other",
        ],
    },
    {
        "id": "state",
        "prompt": "Which state are you in?",
        "options": [
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "Florida",
            "Georgia",
            "Hawaii",
            "Idaho",
            "Illinois",
            "Indiana",
            "Iowa",
            "Kansas",
            "Kentucky",
            "Louisiana",
            "Maine",
            "Maryland",
            "Massachusetts",
            "Michigan",
            "Minnesota",
            "Mississippi",
            "Missouri",
            "Montana",
            "Nebraska",
            "Nevada",
            "New Hampshire",
            "New Jersey",
            "New Mexico",
            "New York",
            "North Carolina",
            "North Dakota",
            "Ohio",
            "Oklahoma",
            "Oregon",
            "Pennsylvania",
            "Rhode Island",
            "South Carolina",
            "South Dakota",
            "Tennessee",
            "Texas",
            "Utah",
            "Vermont",
            "Virginia",
            "Washington",
            "West Virginia",
            "Wisconsin",
            "Wyoming",
            "Other / Prefer not to say",
        ],
    },
    {
        "id": "gpa",
        "prompt": "What is your current GPA?",
        "options": [],
        "type": "other_text",
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
    if q.get("type") == "other_text":
        choice = request.form.get("choice", "").strip()
        if not choice:
            flash("Please enter a short note.", "warning")
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
    if "award_amount" in answers:
        current_user.award_amount = answers["award_amount"]
    if "scholarship_category" in answers:
        current_user.scholarship_category = answers["scholarship_category"]
    if "state" in answers:
        current_user.state = answers["state"]
    if "gpa" in answers:
        # User model may not have a dedicated GPA column in older prototype data.
        # Store it if present; otherwise ignore.
        if hasattr(current_user, "gpa"):
            current_user.gpa = answers["gpa"]
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
