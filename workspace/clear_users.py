from __future__ import annotations

from app import create_app, db
from app.models.user import User


def main() -> None:
    app = create_app()
    with app.app_context():
        db.session.query(User).delete()
        db.session.commit()
        print("Cleared users table")


if __name__ == "__main__":
    main()
