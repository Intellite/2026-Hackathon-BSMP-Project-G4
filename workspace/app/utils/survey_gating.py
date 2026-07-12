from __future__ import annotations

from functools import wraps

from flask import redirect, url_for
from flask_login import current_user


def survey_required(view_func):
    """Lock features until the user completes the survey."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not getattr(current_user, "is_authenticated", False):
            return view_func(*args, **kwargs)

        if not getattr(current_user, "survey_completed", False):
            return redirect(url_for("survey.start"))

        return view_func(*args, **kwargs)

    return wrapper
