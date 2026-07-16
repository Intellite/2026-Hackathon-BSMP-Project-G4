from __future__ import annotations

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.services.ai_service import AIService
from app.services.college_finder import search_colleges
from app.utils.survey_gating import survey_required


college_bp = Blueprint("college", __name__, url_prefix="/college")


COLLEGE_APPLICATIONS: dict[str, dict[str, object]] = {
    "University of California, Berkeley": {
        "slug": "university-of-california-berkeley",
        "application_url": "https://admissions.berkeley.edu/apply/",
        "deadline": "November 30 for UC admission cycle",
        "requirements": [
            "Academic transcripts",
            "Personal insight questions",
            "Coursework history",
            "FAFSA or California Dream Act Application",
        ],
        "notes": "UC applications do not require letters of recommendation for most applicants.",
    },
    "University of Michigan": {
        "slug": "university-of-michigan",
        "application_url": "https://admissions.umich.edu/apply",
        "deadline": "Early Action: November 1; Regular: February 1",
        "requirements": [
            "Official transcripts",
            "Essay responses",
            "Optional test scores",
            "Financial aid forms",
        ],
        "notes": "Check program-specific deadlines for engineering, nursing, and honors programs.",
    },
    "University of Texas at Austin": {
        "slug": "university-of-texas-at-austin",
        "application_url": "https://admissions.utexas.edu/apply/",
        "deadline": "Priority deadline: December 1",
        "requirements": [
            "ApplyTexas application",
            "Official transcripts",
            "Essays",
            "Resume or activity list",
        ],
        "notes": "Some majors may need a portfolio or extra review materials.",
    },
    "Northeastern University": {
        "slug": "northeastern-university",
        "application_url": "https://admissions.northeastern.edu/apply/",
        "deadline": "Early Action and Regular Decision options available",
        "requirements": [
            "Common Application",
            "School report and transcript",
            "Personal essay",
            "Recommendation letters",
        ],
        "notes": "Northeastern uses a holistic review process and may ask for supplemental materials.",
    },
    "Duke University": {
        "slug": "duke-university",
        "application_url": "https://admissions.duke.edu/apply/",
        "deadline": "Early Decision: November 1; Regular Decision: January 2",
        "requirements": [
            "Common Application",
            "School counselor report",
            "Teacher recommendations",
            "Short answer essays",
        ],
        "notes": "Financial aid and interview options may be available depending on region.",
    },
    "University of Washington": {
        "slug": "university-of-washington",
        "application_url": "https://admit.washington.edu/apply/",
        "deadline": "November 15 for first-year applicants",
        "requirements": [
            "UW application",
            "Transcripts",
            "Personal statements",
            "Course planning details",
        ],
        "notes": "Some majors review separately after general admission.",
    },
}


def _get_application_info(college_name: str) -> dict[str, object]:
    base = COLLEGE_APPLICATIONS.get(college_name, {})
    return {
        "slug": base.get("slug") or college_name.lower().replace(" ", "-").replace(",", "").replace(".", ""),
        "application_url": base.get("application_url") or "",
        "deadline": base.get("deadline") or "Check the college admissions site for current deadlines.",
        "requirements": base.get("requirements") or [
            "Official transcript",
            "Personal statement",
            "Application fee or waiver",
        ],
        "notes": base.get("notes") or "Verify program-specific requirements before submitting.",
    }


def _enrich_college(college: dict[str, object]) -> dict[str, object]:
    info = _get_application_info(str(college.get("name", "")))
    enriched = dict(college)
    enriched["application_slug"] = info["slug"]
    enriched["application_url"] = info["application_url"]
    enriched["application_page_url"] = f"/college/apply/{info['slug']}"
    enriched["application_deadline"] = info["deadline"]
    return enriched


def _application_payload(college: dict[str, object]) -> dict[str, object]:
    info = _get_application_info(str(college.get("name", "")))
    slug = str(info["slug"])
    return {
        "name": college.get("name", ""),
        "state": college.get("state", ""),
        "public_private": college.get("public_private", ""),
        "tuition_estimate": college.get("tuition_estimate", ""),
        "url": college.get("url", ""),
        "website_url": college.get("url", ""),
        "application_url": college.get("application_url") or info["application_url"],
        "application_slug": slug,
        "application_page_url": f"/college/apply/{slug}",
        "application_deadline": info["deadline"],
        "requirements": info["requirements"],
        "notes": info["notes"],
    }


def _saved_application_cards() -> list[dict[str, object]]:
    raw = getattr(current_user, "college_applications_json", "") or ""
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    cards: list[dict[str, object]] = []
    for item in data:
        if isinstance(item, dict):
            cards.append(item)
    return cards


def _save_application_cards(cards: list[dict[str, object]]) -> None:
    if hasattr(current_user, "college_applications_json"):
        current_user.college_applications_json = json.dumps(cards)
        db.session.commit()


def _upsert_application(college: dict[str, object]) -> None:
    payload = _application_payload(college)
    cards = _saved_application_cards()
    slug = payload["application_slug"]
    cards = [card for card in cards if card.get("application_slug") != slug]
    cards.append(payload)
    _save_application_cards(cards)


def _find_saved_application(slug: str) -> dict[str, object] | None:
    for card in _saved_application_cards():
        if card.get("application_slug") == slug:
            return card
    return None


def _find_application_by_slug(slug: str) -> dict[str, object] | None:
    for college in search_colleges(limit=6):
        info = _get_application_info(str(college.get("name", "")))
        if info["slug"] == slug:
            return _application_payload(college)

    for name, data in COLLEGE_APPLICATIONS.items():
        if data.get("slug") == slug:
            return _application_payload(
                {
                    "name": name,
                    "state": "",
                    "public_private": "",
                    "tuition_estimate": "",
                    "url": "",
                    "application_url": data.get("application_url", ""),
                }
            )

    return None


@college_bp.get("/")
@login_required
@survey_required
def index() -> str:
    return render_template("dashboard/college_finder.html", results=[])


@college_bp.get("/applications")
@login_required
def applications() -> str:
    return render_template("dashboard/college_applications.html", colleges=_saved_application_cards())


@college_bp.post("/start-application")
@login_required
@survey_required
def start_application() -> str:
    college_name = request.form.get("college_name", "").strip()
    if not college_name:
        flash("Please choose a college to start an application.", "warning")
        return redirect(url_for("college.index"))

    college = {
        "name": college_name,
        "state": request.form.get("state", ""),
        "public_private": request.form.get("public_private", ""),
        "tuition_estimate": request.form.get("tuition_estimate", ""),
        "url": request.form.get("url", ""),
        "application_url": request.form.get("application_url", ""),
    }
    _upsert_application(college)
    flash(f"Started an application for {college_name}.", "success")
    return redirect(url_for("college.applications"))


@college_bp.post("/search")
@login_required
@survey_required
def search() -> str:
    tuition = request.form.get("tuition", "any")
    state = request.form.get("state", "any")
    public_private = request.form.get("public_private", "any")
    major = request.form.get("major", "")

    # Try AI first (parameter-aware). If AI fails/malformed, fall back to demo dataset.
    results = []
    try:
        ai = AIService()
        ai_result = ai.generate_college_matches(
            {
                "filters": {
                    "tuition": tuition,
                    "state": state,
                    "public_private": public_private,
                    "major": major,
                }
            }
        )

        if isinstance(ai_result, dict) and isinstance(ai_result.get("colleges"), list):
            results = ai_result["colleges"][:6]
    except Exception:
        results = []

    if not results:
        results = search_colleges(
            tuition=tuition,
            state=state,
            public_private=public_private,
            major=major,
            limit=6,
        )
    enriched_results = [_enrich_college(college) for college in results]
    return render_template("dashboard/college_finder.html", results=enriched_results)


@college_bp.get("/apply/<college_slug>")
@login_required
def application_page(college_slug: str) -> str:
    college = _find_saved_application(college_slug) or _find_application_by_slug(college_slug)
    if college is None:
        college = {
            "name": "College Application",
            "state": "",
            "public_private": "",
            "tuition_estimate": "",
            "url": "",
            "website_url": "",
            "application_url": "",
            "application_page_url": "",
            "application_deadline": "Check the college admissions site for current deadlines.",
            "requirements": [
                "Official transcript",
                "Personal statement",
                "Application fee or waiver",
            ],
            "notes": "Verify program-specific requirements before submitting.",
        }
    return render_template("dashboard/college_application.html", college=college)


@college_bp.post("/news_summary")
@login_required
@survey_required
def news_summary() -> str:
    college_name = request.form.get("college_name", "")
    college_state = request.form.get("college_state", "")

    ai = AIService()
    result: dict[str, object] = {}
    try:
        result = ai.generate_college_news_summary(
            {
                "college": {
                    "name": college_name,
                    "state": college_state,
                }
            }
        )
    except Exception:
        result = {"college": {"name": college_name, "state": college_state}, "summary_paragraphs": [], "recent_news": []}

    return render_template("dashboard/college_news_summary.html", result=result)
