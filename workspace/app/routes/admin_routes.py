from __future__ import annotations

from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.models.user import User


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin() -> bool:
    return bool(getattr(current_user, "is_admin", False))


@admin_bp.post("/clear-users")
@login_required
def clear_users() -> str:
    if not _require_admin():
        flash("Not authorized.", "danger")
        return redirect(url_for("dashboard.index"))

    # WARNING: destructive action.
    db.session.query(User).delete()
    db.session.commit()

    flash("All user accounts cleared.", "success")
    return redirect(url_for("dashboard.index"))
