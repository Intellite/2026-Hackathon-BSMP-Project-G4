from __future__ import annotations

import argparse

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--email", default=None)
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        existing = db.session.execute(
            db.select(User).where(User.username == args.username)
        ).scalar_one_or_none()

        if existing is not None:
            existing.password_hash = generate_password_hash(args.password)
            existing.email = args.email
            existing.is_admin = True
        else:
            existing = User(
                username=args.username,
                email=args.email,
                password_hash=generate_password_hash(args.password),
                is_admin=True,
            )
            db.session.add(existing)

        db.session.commit()
        print(f"Admin user ready: {existing.username}")


if __name__ == "__main__":
    main()
