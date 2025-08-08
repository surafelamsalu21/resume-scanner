from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
from database.db import db, init_db

# Initialize extensions conditionally
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter_available = True
except ImportError:
    limiter = None
    limiter_available = False

try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf_available = True
except ImportError:
    csrf = None
    csrf_available = False


def create_app(config_name=None):
    """
    Application factory function that creates and configures the Flask application.

    Args:
        config_name (str): The name of the configuration to use (development, production, testing)

    Returns:
        Flask: The configured Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Fix the configuration import path
    from config.config import config_dict
    app.config.from_object(config_dict[config_name.lower()])

    # Configure logging
    configure_logging(app)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('ALLOWED_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"]
        }
    })

    # Initialize extensions
    init_db(app)

    # Initialize rate limiter if available
    if limiter_available and app.config.get('RATELIMIT_ENABLED', False):
        try:
            limiter.init_app(app)
            app.logger.info("Rate limiting enabled")
        except Exception as e:
            app.logger.warning(f"Failed to initialize rate limiter: {str(e)}")
    else:
        app.logger.info("Rate limiting disabled")

    # Initialize CSRF protection if available
    if csrf_available:
        try:
            csrf.init_app(app)
            # Exempt API routes from CSRF protection
            csrf_exempt_blueprints = ['resume_bp', 'ranking_bp', 'admin_bp']
            app.logger.info("CSRF protection enabled")
        except Exception as e:
            app.logger.warning(
                f"Failed to initialize CSRF protection: {str(e)}")
    else:
        app.logger.info("CSRF protection disabled")
        csrf_exempt_blueprints = []

    # Register blueprints
    register_blueprints(app, csrf_exempt_blueprints)

    # Register error handlers
    register_error_handlers(app)

    # Register health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': os.getenv('APP_VERSION', '1.0.0')
        })

    # Register home route
    @app.route('/')
    def home():
        """Home page"""
        return render_template('index.html')

    app.logger.info('Resume AI Backend startup complete')
    return app


def configure_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        file_handler = RotatingFileHandler(
            'logs/resume_ai.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Resume AI Backend logging configured')


def register_blueprints(app, csrf_exempt_blueprints=None):
    """Register Flask blueprints."""
    from .routes.resume import resume_bp
    from .routes.ranking import ranking_bp
    from admin import init_admin

    # Register blueprints
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(ranking_bp, url_prefix='/api/ranking')

    # Initialize admin blueprint last
    init_admin(app)

    # Exempt API routes from CSRF protection if CSRF is enabled
    if csrf and csrf_exempt_blueprints:
        for blueprint_name in csrf_exempt_blueprints:
            try:
                csrf.exempt(eval(blueprint_name))
            except Exception as e:
                app.logger.warning(
                    f"Failed to exempt {blueprint_name} from CSRF: {str(e)}")

    app.logger.info('Blueprints registered')


def register_error_handlers(app):
    """Register error handlers for the application."""

    @app.errorhandler(400)
    def bad_request_error(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
        return render_template('error.html',
                               error_title='Bad Request',
                               error_message='The request could not be understood by the server.'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        return render_template('error.html',
                               error_title='Unauthorized',
                               error_message='Authentication is required to access this resource.'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}), 403
        return render_template('error.html',
                               error_title='Forbidden',
                               error_message='You do not have permission to access this resource.'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found'}), 404
        return render_template('error.html',
                               error_title='Page Not Found',
                               error_message='The page you are looking for does not exist.'), 404

    @app.errorhandler(429)
    def ratelimit_error(error):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded'}), 429
        return render_template('error.html',
                               error_title='Too Many Requests',
                               error_message='You have made too many requests. Please try again later.'), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500
        return render_template('error.html',
                               error_title='Server Error',
                               error_message='An unexpected error occurred. Our team has been notified.'), 500

    app.logger.info('Error handlers registered')

# Make the database instance available at the package level
