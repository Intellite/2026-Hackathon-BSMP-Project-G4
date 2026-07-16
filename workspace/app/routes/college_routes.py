from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.services.college_finder import search_colleges
from app.services.ai_service import AIService
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


def _application_entries() -> list[dict[str, object]]:
    colleges = search_colleges(limit=6)
    return [_enrich_college(college) for college in colleges]


@college_bp.get("/")
@login_required
@survey_required
def index() -> str:
    return render_template("dashboard/college_finder.html", results=[])


@college_bp.get("/applications")
@login_required
def applications() -> str:
    return render_template("dashboard/college_applications.html", colleges=_application_entries())


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
    college = next((entry for entry in _application_entries() if entry["application_slug"] == college_slug), None)
    if college is None:
        college = {
            "name": "College Application",
            "state": "",
            "public_private": "",
            "tuition_estimate": "",
            "match_score": 0,
            "url": "",
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
