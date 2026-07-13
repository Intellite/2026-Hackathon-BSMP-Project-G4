from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import requests

from config import Config

# Ensure .env is loaded when running via scripts/tests.
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class AIResult:
    raw: Any


class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = max(1, per_minute)
        self.window_start = time.time()
        self.count = 0

    def allow(self) -> bool:
        now = time.time()
        if now - self.window_start >= 60:
            self.window_start = now
            self.count = 0
        if self.count >= self.per_minute:
            return False
        self.count += 1
        return True


class AIService:
    """AI abstraction layer for OpenAI-compatible endpoints.

    For hackathon demo: if AI_API_KEY is missing, returns deterministic mock outputs.
    """

    def __init__(self) -> None:
        self.cfg = Config
        self.rate_limiter = RateLimiter(self.cfg.AI_RATE_LIMIT_PER_MINUTE)

        # Provider selection
        self._use_azure = bool(self.cfg.AZURE_OPENAI_ENDPOINT and self.cfg.AZURE_OPENAI_API_KEY)

    def _prompt_path(self, name: str) -> Path:
        return Path(__file__).resolve().parent / "prompts" / f"{name}.txt"

    def _load_prompt(self, name: str) -> str:
        p = self._prompt_path(name)
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""

    def _call_openai_compatible(self, messages: list[dict[str, str]]) -> str:
        if not self.cfg.AI_API_KEY or not self.cfg.AI_BASE_URL:
            return ""

        url = self.cfg.AI_BASE_URL.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.cfg.AI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.cfg.AI_MODEL,
            "messages": messages,
            "temperature": 0.4,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _call_azure_openai(self, messages: list[dict[str, str]]) -> str:
        if not self.cfg.AZURE_OPENAI_ENDPOINT or not self.cfg.AZURE_OPENAI_API_KEY:
            return ""

        deployment = self.cfg.AZURE_OPENAI_DEPLOYMENT or self.cfg.AI_MODEL
        if not deployment:
            return ""

        # Azure OpenAI chat completions endpoint
        # Example: https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview
        base = self.cfg.AZURE_OPENAI_ENDPOINT.rstrip("/")
        # Try a couple of common api versions for Azure OpenAI.
        api_versions = ["2024-02-15-preview", "2024-06-01"]

        headers = {
            "api-key": self.cfg.AZURE_OPENAI_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "messages": messages,
            "temperature": 0.4,
        }

        last_err: Exception | None = None
        for api_version in api_versions:
            url = f"{base}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue

        raise last_err or RuntimeError("Azure OpenAI call failed")

    def _call_chat(self, messages: list[dict[str, str]]) -> str:
        if self._use_azure:
            return self._call_azure_openai(messages)
        return self._call_openai_compatible(messages)

    def _with_retry(self, fn: Callable[[], str], retries: int = 2) -> str:
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                return fn()
            except Exception as e:  # noqa: BLE001
                last_err = e
                wait = 0.8 * (attempt + 1)
                logger.warning("AI call failed (attempt %s): %s", attempt + 1, e)
                time.sleep(wait)
        raise last_err or RuntimeError("AI call failed")

    def _ensure_rate_limit(self) -> None:
        if not self.rate_limiter.allow():
            raise RuntimeError("Rate limit exceeded. Please try again shortly.")

    def generate_career_matches(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_rate_limit()
        prompt = self._load_prompt("generate_career_matches")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            return {
                "careers": [
                    {
                        "title": "Software Engineer",
                        "match_percentage": 86,
                        "salary_low": 65000,
                        "salary_high": 120000,
                        "education": "Computer Science or related",
                        "description": "Build apps, solve problems, and create impact.",
                        "required_skills": "Python, JavaScript, teamwork, problem-solving",
                    },
                    {
                        "title": "Data Analyst",
                        "match_percentage": 74,
                        "salary_low": 55000,
                        "salary_high": 95000,
                        "education": "Statistics / Data Science",
                        "description": "Turn data into decisions and insights.",
                        "required_skills": "SQL, spreadsheets, communication",
                    },
                    {
                        "title": "Healthcare Administrator",
                        "match_percentage": 68,
                        "salary_low": 52000,
                        "salary_high": 90000,
                        "education": "Public Health / Business",
                        "description": "Improve systems that support patients and staff.",
                        "required_skills": "Leadership, organization, communication",
                    },
                ]
            }

        messages = [
            {"role": "system", "content": prompt or "You are a helpful career advisor."},
            {"role": "user", "content": json.dumps(payload)},
        ]

        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"careers": []}

    def generate_roadmap(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_rate_limit()
        prompt = self._load_prompt("generate_roadmap")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            return {
                "roadmap": [
                    {
                        "phase": "High School Phase",
                        "summary": "Build foundations and proof-of-skill projects.",
                        "steps": [
                            "Join a relevant club (robotics, coding, debate)",
                            "Complete 2 portfolio projects",
                            "Seek a mentor and practice interviews",
                        ],
                    },
                    {
                        "phase": "College/Certification Phase",
                        "summary": "Earn credentials and internship experience.",
                        "steps": [
                            "Take core coursework",
                            "Apply for internships",
                            "Build a resume + LinkedIn presence",
                        ],
                    },
                    {
                        "phase": "Early Career Phase",
                        "summary": "Grow through entry roles and mentorship.",
                        "steps": [
                            "Ship measurable work",
                            "Ask for feedback",
                            "Network with professionals",
                        ],
                    },
                    {
                        "phase": "Advanced Career Phase",
                        "summary": "Lead, specialize, and expand impact.",
                        "steps": [
                            "Take leadership opportunities",
                            "Specialize in a niche",
                            "Mentor others",
                        ],
                    },
                ]
            }

        messages = [
            {"role": "system", "content": prompt or "You generate structured roadmaps."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"roadmap": []}

    def generate_college_matches(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return AI-generated college matches as strict JSON."""
        self._ensure_rate_limit()
        prompt = self._load_prompt("generate_college_matches")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            # Deterministic fallback (demo)
            return {
                "colleges": [
                    {
                        "name": "University of California, Berkeley",
                        "state": "CA",
                        "public_private": "Public",
                        "tuition_estimate": "$15k-$18k/yr",
                        "acceptable_rates": {
                            "resident": "$15k-$18k/yr",
                            "non_resident": "$35k-$40k/yr",
                            "average": "$25k-$29k/yr",
                        },
                        "url": "https://www.berkeley.edu/",
                        "match_score": 90,
                    }
                ]
            }

        messages = [
            {"role": "system", "content": prompt or "You recommend colleges."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"colleges": []}

    def analyze_skill_gaps(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_rate_limit()
        prompt = self._load_prompt("analyze_skill_gaps")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            return {
                "gaps": [
                    {"name": "Python Skill", "current_percent": 80},
                    {"name": "Leadership", "current_percent": 40},
                    {"name": "Internship Experience", "current_percent": 20},
                ],
                "suggested_activities": [
                    "Build a small project and present it",
                    "Join a leadership role in a club",
                    "Apply for a summer internship or shadowing",
                ],
            }

        messages = [
            {"role": "system", "content": prompt or "You analyze skill gaps."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"gaps": [], "suggested_activities": []}

    def recommend_scholarships(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_rate_limit()
        prompt = self._load_prompt("recommend_scholarships")
        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            return {"recommendations": []}
        messages = [
            {"role": "system", "content": prompt or "You recommend scholarships."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"recommendations": []}

    def chat_with_mentor(self, payload: dict[str, Any]) -> str:
        self._ensure_rate_limit()
        prompt = self._load_prompt("chat_with_mentor")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            msg = payload.get("message", "")
            return (
                "Thanks for asking!\n\n"
                "For your next step: pick one small action you can complete this week. "
                "Then ask me to turn it into a roadmap.\n\n"
                f"You asked: {msg}"
            )

        messages = [
            {"role": "system", "content": prompt or "You are a supportive student mentor."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        return self._with_retry(lambda: self._call_chat(messages))

    def analyze_resume(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_rate_limit()
        prompt = self._load_prompt("analyze_resume")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            return {
                "score": 78,
                "strengths": [
                    "Clear summary of goals",
                    "Relevant experience highlights",
                    "Good formatting",
                ],
                "weaknesses": [
                    "Limited measurable impact",
                    "Skills section could be more specific",
                ],
                "improvements": [
                    "Add 2-3 quantified achievements",
                    "Tailor skills to the target career",
                    "Use action verbs and strong bullet structure",
                ],
                "skill_recommendations": ["Python", "Communication", "Project portfolio"],
            }

        messages = [
            {"role": "system", "content": prompt or "You analyze resumes and return JSON."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"score": 0, "strengths": [], "weaknesses": [], "improvements": [], "skill_recommendations": []}

    def generate_future_projection(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_rate_limit()
        prompt = self._load_prompt("generate_future_projection")

        if not (self.cfg.AI_API_KEY and self.cfg.AI_BASE_URL) and not self._use_azure:
            return {
                "timeline": [
                    {"stage": "Intern", "salary": 45000},
                    {"stage": "Entry Level", "salary": 65000},
                    {"stage": "Mid-Level", "salary": 90000},
                    {"stage": "Senior", "salary": 125000},
                ]
            }

        messages = [
            {"role": "system", "content": prompt or "You generate future earnings projections."},
            {"role": "user", "content": json.dumps(payload)},
        ]
        text = self._with_retry(lambda: self._call_chat(messages))
        try:
            return json.loads(text)
        except Exception:
            return {"timeline": []}
