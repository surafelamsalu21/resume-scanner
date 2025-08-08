from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os
import sqlalchemy as sa
import sqlite3

# Configure logging
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initialize the database with the Flask app.

    Args:
        app: Flask application instance

    Returns:
        None

    Raises:
        Exception: If database initialization fails
    """
    try:
        # Initialize SQLAlchemy
        db.init_app(app)

        # Initialize Flask-Migrate
        migrate.init_app(app, db)

        with app.app_context():
            # Check if using SQLite and create directory if needed
            if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace(
                    'sqlite:///', '')
                db_dir = os.path.dirname(os.path.abspath(db_path))
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)

                # Enable foreign key support for SQLite
                @sa.event.listens_for(sa.engine.Engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    if isinstance(dbapi_connection, sqlite3.Connection):
                        cursor = dbapi_connection.cursor()
                        cursor.execute("PRAGMA foreign_keys=ON")
                        cursor.close()

            # Create all tables if they don't exist
            db.create_all()

            # Log successful initialization
            logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
