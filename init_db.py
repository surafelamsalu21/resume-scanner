from app import create_app
from database.db import db
import os

# Create app with development configuration
app = create_app('development')

# Push application context
with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")

    # Create uploads directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Created uploads directory: {app.config['UPLOAD_FOLDER']}")
    else:
        print(
            f"Uploads directory already exists: {app.config['UPLOAD_FOLDER']}")
