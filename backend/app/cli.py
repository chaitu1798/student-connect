import argparse
import sys
import getpass
import secrets
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.utils.security import hash_password

def bootstrap_admin(username: str, email: str, password: str | None = None, force: bool = False):
    """
    Securely creates or resets the initial SUPER_ADMIN user without logging credentials.
    Suitable for production initialization and CI/CD deployment pipelines.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and not force:
            print(f"Error: User '{username}' already exists. Use --force to update.", file=sys.stderr)
            sys.exit(1)

        generated = False
        if not password:
            if sys.stdin.isatty():
                password = getpass.getpass(f"Enter password for admin '{username}': ")
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    print("Error: Passwords do not match.", file=sys.stderr)
                    sys.exit(1)
            else:
                # Non-interactive generation
                password = secrets.token_urlsafe(24)
                generated = True

        if len(password) < 8:
            print("Error: Password must be at least 8 characters long.", file=sys.stderr)
            sys.exit(1)

        hashed = hash_password(password)

        if user:
            user.email = email
            user.role = "SUPER_ADMIN"
            user.hashed_password = hashed
            user.is_active = True
            user.must_change_password = False
            action = "updated"
        else:
            user = User(
                username=username,
                email=email,
                full_name="System Administrator",
                role="SUPER_ADMIN",
                hashed_password=hashed,
                is_active=True,
                must_change_password=False,
                mfa_enabled=False,
            )
            db.add(user)
            action = "created"

        db.commit()
        print(f"Successfully {action} SUPER_ADMIN user '{username}' ({email}).")
        if generated:
            print("Generated temporary password (keep secure and change immediately):")
            print(password)
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Institutional Student Portal Administrative CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # bootstrap-admin
    bootstrap_parser = subparsers.add_parser("bootstrap-admin", help="Bootstrap initial SUPER_ADMIN account")
    bootstrap_parser.add_argument("--username", default="admin", help="Administrator username (default: admin)")
    bootstrap_parser.add_argument("--email", default="admin@institution.edu", help="Administrator email")
    bootstrap_parser.add_argument("--password", default=None, help="Administrator password (prompted if omitted)")
    bootstrap_parser.add_argument("--force", action="store_true", help="Force update if user already exists")

    args = parser.parse_args()

    if args.command == "bootstrap-admin":
        bootstrap_admin(username=args.username, email=args.email, password=args.password, force=args.force)

if __name__ == "__main__":
    main()
