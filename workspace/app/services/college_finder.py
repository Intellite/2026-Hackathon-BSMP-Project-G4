from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CollegeResult:
    name: str
    state: str
    public_private: str
    tuition_estimate: str
    acceptable_rates: dict[str, str]
    url: str
    match_score: int


def search_colleges(
    *,
    tuition: str | None = None,
    state: str | None = None,
    public_private: str | None = None,
    major: str | None = None,
    limit: int = 6,
) -> list[dict[str, Any]]:
    """Simple in-app college finder.

    Note: This is a demo dataset (no external API calls).
    """

    # Demo dataset
    colleges: list[CollegeResult] = [
        CollegeResult(
            name="University of California, Berkeley",
            state="CA",
            public_private="Public",
            tuition_estimate="$15k-$18k/yr",
            acceptable_rates={
                "resident": "$15k-$18k/yr",
                "non_resident": "$35k-$40k/yr",
                "average": "$25k-$29k/yr",
            },
            url="https://www.berkeley.edu/",
            match_score=92,
        ),
        CollegeResult(
            name="University of Michigan",
            state="MI",
            public_private="Public",
            tuition_estimate="$14k-$17k/yr",
            acceptable_rates={
                "resident": "$14k-$17k/yr",
                "non_resident": "$33k-$38k/yr",
                "average": "$24k-$28k/yr",
            },
            url="https://umich.edu/",
            match_score=86,
        ),
        CollegeResult(
            name="University of Texas at Austin",
            state="TX",
            public_private="Public",
            tuition_estimate="$12k-$16k/yr",
            acceptable_rates={
                "resident": "$12k-$16k/yr",
                "non_resident": "$30k-$36k/yr",
                "average": "$21k-$26k/yr",
            },
            url="https://www.utexas.edu/",
            match_score=84,
        ),
        CollegeResult(
            name="Northeastern University",
            state="MA",
            public_private="Private",
            tuition_estimate="$55k-$60k/yr",
            acceptable_rates={
                "resident": "$55k-$60k/yr",
                "non_resident": "$55k-$60k/yr",
                "average": "$55k-$60k/yr",
            },
            url="https://www.northeastern.edu/",
            match_score=78,
        ),
        CollegeResult(
            name="Duke University",
            state="NC",
            public_private="Private",
            tuition_estimate="$60k-$65k/yr",
            acceptable_rates={
                "resident": "$60k-$65k/yr",
                "non_resident": "$60k-$65k/yr",
                "average": "$60k-$65k/yr",
            },
            url="https://www.duke.edu/",
            match_score=74,
        ),
        CollegeResult(
            name="University of Washington",
            state="WA",
            public_private="Public",
            tuition_estimate="$14k-$18k/yr",
            acceptable_rates={
                "resident": "$14k-$18k/yr",
                "non_resident": "$32k-$38k/yr",
                "average": "$23k-$28k/yr",
            },
            url="https://www.washington.edu/",
            match_score=80,
        ),
    ]

    def tuition_matches(c: CollegeResult) -> bool:
        # Demo logic:
        # - If user enters a number, treat it as a rough max tuition and map to Public/Private.
        # - If user enters non-numeric text (e.g., "any"), fall back to no filtering.
        if not tuition or tuition == "any":
            return True

        t = str(tuition).strip().lower()
        try:
            max_tuition = float(t)
        except ValueError:
            return True

        # Rough thresholds for demo purposes.
        if max_tuition <= 20000:
            return c.public_private == "Public"
        if max_tuition <= 45000:
            return c.public_private in {"Public", "Private"}
        return c.public_private == "Private"

    filtered: list[CollegeResult] = []
    for c in colleges:
        if state and state != "any" and c.state.upper() != state.upper():
            continue
        if public_private and public_private != "any" and c.public_private != public_private:
            continue
        if not tuition_matches(c):
            continue
        filtered.append(c)

    filtered.sort(key=lambda x: x.match_score, reverse=True)
    return [
        {
            "name": c.name,
            "state": c.state,
            "public_private": c.public_private,
            "tuition_estimate": c.tuition_estimate,
            "acceptable_rates": c.acceptable_rates,
            "url": c.url,
            "match_score": c.match_score,
        }
        for c in filtered[:limit]
    ]
