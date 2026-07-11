from __future__ import annotations

from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def home() -> str:
    return render_template("home.html")
