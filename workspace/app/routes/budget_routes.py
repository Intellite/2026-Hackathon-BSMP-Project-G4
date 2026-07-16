from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import login_required

budget_bp = Blueprint("budget", __name__, url_prefix="/budget")


@budget_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    result = None

    if request.method == "POST":
        def to_float(name: str) -> float:
            val = request.form.get(name, "0")
            try:
                return float(val)
            except ValueError:
                return 0.0

        income = to_float("income")
        savings = to_float("savings")
        tuition = to_float("tuition")
        housing = to_float("housing")
        transport = to_float("transport")
        other = to_float("other")

        total_costs = tuition + housing + transport + other
        remaining = income - total_costs - savings

        if remaining >= 0:
            affordability = "Likely affordable"
        else:
            affordability = "May be tight—consider scholarships or adjustments"

        result = {
            "total_costs": f"${total_costs:,.2f}",
            "remaining": f"${remaining:,.2f}",
            "affordability": affordability,
        }

    return render_template("budget/index.html", result=result)
