from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.get("/")
@login_required
def index() -> str:
    return render_template("profile/settings.html")
