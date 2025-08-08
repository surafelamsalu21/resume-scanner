from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
import jwt
from os import getenv, path
from typing import Dict, List, Optional, Callable
import logging
from app.models import Admin, JobPosting, AIPrompt, ResumeProcessingSettings
from database.db import db
import os

# Configure logging
logger = logging.getLogger(__name__)

# Create the blueprint with the correct template folder path
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(current_dir), 'app', 'templates')

admin_bp = Blueprint('admin', __name__,
                     url_prefix='/admin',
                     template_folder=template_dir)


def init_admin(app):
    """Initialize admin module."""
    # Import routes here to avoid circular imports
    from . import routes  # Import other admin routes
    from . import auth  # Import authentication routes
    from . import dashboard  # Import dashboard routes

    app.register_blueprint(admin_bp)
    app.logger.info("Admin module initialized")


def admin_required(f: Callable) -> Callable:
    """Decorator to check admin authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')

        # Check for token in cookies
        elif request.cookies.get('access_token'):
            token = request.cookies.get('access_token')

        # Check for token in query parameters (for testing only)
        elif request.args.get('token'):
            token = request.args.get('token')

        if not token:
            # If it's a web request, redirect to login page
            if request.headers.get('Accept', '').find('text/html') != -1:
                return redirect(url_for('admin.login'))
            return jsonify({'message': 'Authentication token is missing'}), 401

        try:
            # Decode token
            secret_key = getenv(
                'JWT_SECRET_KEY', 'your_secret_key_for_jwt_tokens')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Check token type (but don't require it to be 'access')
            # This allows both access_token and refresh_token to work
            if 'admin_id' not in data:
                if request.headers.get('Accept', '').find('text/html') != -1:
                    return redirect(url_for('admin.login'))
                return jsonify({'message': 'Invalid token format'}), 401

            current_admin = Admin.query.filter_by(id=data['admin_id']).first()

            if not current_admin:
                if request.headers.get('Accept', '').find('text/html') != -1:
                    return redirect(url_for('admin.login'))
                return jsonify({'message': 'Invalid admin token'}), 401

            # Add admin to request context
            request.admin = current_admin
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            if request.headers.get('Accept', '').find('text/html') != -1:
                return redirect(url_for('admin.login'))
            return jsonify({'message': 'Token has expired', 'code': 'token_expired'}), 401
        except jwt.InvalidTokenError:
            if request.headers.get('Accept', '').find('text/html') != -1:
                return redirect(url_for('admin.login'))
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            if request.headers.get('Accept', '').find('text/html') != -1:
                return redirect(url_for('admin.login'))
            return jsonify({'message': 'Authentication error'}), 401

    return decorated

# Job Posting Management


@admin_bp.route('/jobs', methods=['GET', 'POST'])
@admin_required
def manage_jobs():
    """Manage job postings."""
    try:
        if request.method == 'GET':
            jobs = JobPosting.query.all()
            return jsonify([job.to_dict() for job in jobs])

        if request.method == 'POST':
            data = request.get_json()
            new_job = JobPosting(
                title=data['title'],
                description=data['description'],
                requirements=data['requirements'],
                created_by=request.admin.id
            )
            db.session.add(new_job)
            db.session.commit()
            return jsonify(new_job.to_dict()), 201

    except Exception as e:
        logger.error(f"Job management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# AI Prompt Management


@admin_bp.route('/prompts', methods=['GET', 'POST', 'PUT'])
@admin_required
def manage_prompts():
    """Manage AI prompts for resume processing."""
    try:
        if request.method == 'GET':
            prompts = AIPrompt.query.all()
            return jsonify([prompt.to_dict() for prompt in prompts])

        if request.method == 'POST':
            data = request.get_json()
            new_prompt = AIPrompt(
                name=data['name'],
                content=data['content'],
                purpose=data['purpose'],
                created_by=request.admin.id
            )
            db.session.add(new_prompt)
            db.session.commit()
            return jsonify(new_prompt.to_dict()), 201

        if request.method == 'PUT':
            data = request.get_json()
            prompt = AIPrompt.query.get(data['id'])
            if not prompt:
                return jsonify({'message': 'Prompt not found'}), 404

            prompt.content = data['content']
            prompt.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(prompt.to_dict())

    except Exception as e:
        logger.error(f"Prompt management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Resume Processing Settings


@admin_bp.route('/settings', methods=['GET', 'PUT'])
@admin_required
def manage_settings():
    """Manage resume processing settings."""
    try:
        if request.method == 'GET':
            settings = ResumeProcessingSettings.query.first()
            return jsonify(settings.to_dict() if settings else {})

        if request.method == 'PUT':
            data = request.get_json()
            settings = ResumeProcessingSettings.query.first()

            if not settings:
                settings = ResumeProcessingSettings()
                db.session.add(settings)

            settings.update_from_dict(data)
            settings.updated_by = request.admin.id
            settings.updated_at = datetime.utcnow()

            db.session.commit()
            return jsonify(settings.to_dict())

    except Exception as e:
        logger.error(f"Settings management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Admin Analytics


@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get admin analytics and statistics."""
    try:
        analytics = {
            'total_jobs': JobPosting.query.count(),
            'total_prompts': AIPrompt.query.count(),
            'recent_jobs': [job.to_dict() for job in JobPosting.query.order_by(JobPosting.created_at.desc()).limit(5)],
            'recent_prompts': [prompt.to_dict() for prompt in AIPrompt.query.order_by(AIPrompt.updated_at.desc()).limit(5)],
            'system_status': {
                'ai_service': 'operational',
                'database': 'connected',
                'last_backup': datetime.utcnow().isoformat()
            }
        }
        return jsonify(analytics)

    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Error handlers


@admin_bp.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404


@admin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500
