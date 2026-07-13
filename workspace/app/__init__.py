from __future__ import annotations

import logging
import os
from logging.config import dictConfig

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # Logging
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {"level": app.config.get("LOG_LEVEL", "INFO"), "handlers": ["console"]},
        }
    )

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from app.routes.home_routes import home_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.survey_routes import survey_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.careers_routes import careers_bp
    from app.routes.roadmap_routes import roadmap_bp
    from app.routes.gap_routes import gap_bp
    from app.routes.scholarships_routes import scholarships_bp
    from app.routes.mentor_routes import mentor_bp
    from app.routes.resume_routes import resume_bp
    from app.routes.college_routes import college_bp
    from app.routes.profile_routes import profile_bp
    from app.routes.settings_routes import settings_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(careers_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(gap_bp)
    app.register_blueprint(scholarships_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(college_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)

    # Create tables
    with app.app_context():
        from app.models import user, career, scholarship, conversation

        db.create_all()

        # Seed demo data (hackathon)
        try:
            from app.utils.seed_data import seed

            seed()
        except Exception as e:  # noqa: BLE001
            logging.getLogger(__name__).warning("Seed skipped: %s", e)

    return app
