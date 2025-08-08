from flask import render_template, jsonify, current_app, request
from app.models import Admin, Resume, JobCategory, AIPrompt, AdminActivity
import logging
from admin import admin_bp, admin_required

# Configure logging
logger = logging.getLogger(__name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    """Admin dashboard page."""
    try:
        # Log access to dashboard
        logger.info("Dashboard route accessed from dashboard.py")

        # Get basic stats for the dashboard
        stats = {
            'users': Admin.query.count(),
            'resumes': Resume.query.count(),
            'categories': JobCategory.query.count(),
            'prompts': AIPrompt.query.count()
        }

        logger.info(f"Dashboard stats: {stats}")

        # Get recent activities
        recent_activities = AdminActivity.query.order_by(
            AdminActivity.created_at.desc()).limit(5).all()

        logger.info(f"Recent activities count: {len(recent_activities)}")

        # Get recent job categories
        job_categories = JobCategory.query.order_by(
            JobCategory.created_at.desc()).limit(10).all()

        logger.info(f"Job categories count: {len(job_categories)}")

        # Get recent AI prompts
        ai_prompts = AIPrompt.query.order_by(
            AIPrompt.updated_at.desc()).limit(10).all()

        logger.info(f"AI prompts count: {len(ai_prompts)}")

        # Use the admin from the request
        return render_template(
            'admin_dashboard.html',
            stats=stats,
            recent_activities=recent_activities,
            job_categories=job_categories,
            ai_prompts=ai_prompts,
            admin=request.admin
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        # Return a simple response for debugging
        return f"Dashboard error: {str(e)}", 500
