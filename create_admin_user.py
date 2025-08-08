from app import create_app
from app.models import Admin, db
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app('development')
with app.app_context():
    # Check if admin exists
    admin = Admin.query.filter_by(email='admin@example.com').first()

    if admin:
        # Update existing admin
        admin.password_hash = generate_password_hash('admin123')
        print("Admin password updated")
    else:
        # Create new admin
        admin = Admin(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        print("New admin user created")

    db.session.commit()
    print("Admin user saved successfully")
