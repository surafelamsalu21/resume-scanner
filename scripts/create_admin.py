#!/usr/bin/env python3
"""
Script to create an admin user for the Resume AI Backend.
Run this script after setting up the database to create the initial admin user.
"""

import os
import sys
from dotenv import load_dotenv
import argparse
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()


def create_admin(username, email, password):
    """Create an admin user in the database"""
    try:
        # Import here to avoid circular imports
        from app import create_app
        from database.db import db
        from app.models import Admin

        # Create app context
        app = create_app(os.getenv('FLASK_ENV', 'development'))

        with app.app_context():
            # Check if admin already exists
            existing_admin = Admin.query.filter_by(email=email).first()
            if existing_admin:
                print(f"Admin with email {email} already exists.")
                return False

            # Create new admin
            admin = Admin(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_active=True,
                created_at=datetime.utcnow()
            )

            db.session.add(admin)
            db.session.commit()

            print(f"Admin user created successfully: {username} ({email})")
            return True

    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        return False


def main():
    """Main function to parse arguments and create admin"""
    parser = argparse.ArgumentParser(
        description='Create an admin user for Resume AI Backend')
    parser.add_argument('--username', default=os.getenv('ADMIN_USERNAME', 'admin'),
                        help='Admin username (default: from ADMIN_USERNAME env var or "admin")')
    parser.add_argument('--email', default=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
                        help='Admin email (default: from ADMIN_EMAIL env var or "admin@example.com")')
    parser.add_argument('--password', default=os.getenv('ADMIN_PASSWORD'),
                        help='Admin password (default: from ADMIN_PASSWORD env var)')

    args = parser.parse_args()

    # Validate inputs
    if not args.email or '@' not in args.email:
        print("Error: Valid email is required")
        sys.exit(1)

    if not args.password:
        print(
            "Error: Password is required. Set it with --password or ADMIN_PASSWORD env var")
        sys.exit(1)

    # Create admin user
    success = create_admin(args.username, args.email, args.password)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
