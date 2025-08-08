from flask import request, jsonify, render_template, redirect, url_for, current_app
from datetime import datetime
from app.models import Admin, JobPosting, AIPrompt, AdminActivity, JobCategory, db, Resume, ProcessedResume
import logging
from admin import admin_bp, admin_required
from functools import wraps
from app.utils import AIProcessor
from app.services import AIService, ResumeProcessor
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Test route - no authentication required


@admin_bp.route('/test', methods=['GET'])
def test_route():
    """Test route to verify routing is working."""
    return jsonify({"message": "Admin test route is working!"}), 200


# Index route - redirects to dashboard
@admin_bp.route('/', methods=['GET'])
def index():
    """Admin index route that redirects to dashboard."""
    return redirect(url_for('admin.dashboard'))


# Another test route
@admin_bp.route('/dashboard2', methods=['GET'])
def dashboard2():
    """Another test route for the dashboard."""
    return jsonify({"message": "Dashboard2 route is working!"}), 200

# Job Management Routes


@admin_bp.route('/jobs/<int:job_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def manage_job(job_id: int):
    """Manage individual job postings."""
    try:
        job = JobPosting.query.get_or_404(job_id)

        if request.method == 'GET':
            return jsonify(job.to_dict())

        if request.method == 'PUT':
            data = request.get_json()
            job.title = data.get('title', job.title)
            job.description = data.get('description', job.description)
            job.requirements = data.get('requirements', job.requirements)
            job.category_id = data.get('category_id', job.category_id)
            job.status = data.get('status', job.status)
            job.updated_by = request.admin.id
            job.updated_at = datetime.utcnow()

            # Log admin activity
            activity = AdminActivity(
                admin_id=request.admin.id,
                action='update_job',
                details=f'Updated job posting: {job.title}'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify(job.to_dict())

        if request.method == 'DELETE':
            db.session.delete(job)

            # Log admin activity
            activity = AdminActivity(
                admin_id=request.admin.id,
                action='delete_job',
                details=f'Deleted job posting: {job.title}'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({'message': 'Job deleted successfully'})

    except Exception as e:
        logger.error(f"Job management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/jobs/categories', methods=['GET', 'POST'])
@admin_required
def manage_job_categories():
    """Manage job categories."""
    try:
        if request.method == 'GET':
            categories = JobCategory.query.all()
            return jsonify([category.to_dict() for category in categories])

        if request.method == 'POST':
            data = request.get_json()
            new_category = JobCategory(
                name=data['name'],
                description=data.get('description', '')
            )
            db.session.add(new_category)
            db.session.commit()
            return jsonify(new_category.to_dict()), 201

    except Exception as e:
        logger.error(f"Category management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# AI Prompt Management Routes


@admin_bp.route('/prompts/<int:prompt_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def manage_prompt(prompt_id: int):
    """Manage individual AI prompts."""
    try:
        prompt = AIPrompt.query.get_or_404(prompt_id)

        if request.method == 'GET':
            return jsonify(prompt.to_dict())

        if request.method == 'PUT':
            data = request.get_json()
            prompt.name = data.get('name', prompt.name)
            prompt.content = data.get('content', prompt.content)
            prompt.purpose = data.get('purpose', prompt.purpose)
            prompt.updated_by = request.admin.id
            prompt.updated_at = datetime.utcnow()

            # Log admin activity
            activity = AdminActivity(
                admin_id=request.admin.id,
                action='update_prompt',
                details=f'Updated AI prompt: {prompt.name}'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify(prompt.to_dict())

        if request.method == 'DELETE':
            db.session.delete(prompt)

            # Log admin activity
            activity = AdminActivity(
                admin_id=request.admin.id,
                action='delete_prompt',
                details=f'Deleted AI prompt: {prompt.name}'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({'message': 'Prompt deleted successfully'})

    except Exception as e:
        logger.error(f"Prompt management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/prompts/test', methods=['POST'])
@admin_required
def test_prompt():
    """Test AI prompt with sample data."""
    try:
        data = request.get_json()
        prompt_id = data.get('prompt_id')
        test_data = data.get('test_data')

        prompt = AIPrompt.query.get_or_404(prompt_id)
        ai_processor = AIProcessor()

        # Test the prompt with sample data
        result = ai_processor.test_prompt(prompt.content, test_data)

        # Log the test
        activity = AdminActivity(
            admin_id=request.admin.id,
            action='test_prompt',
            details=f'Tested AI prompt: {prompt.name}'
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'prompt_name': prompt.name,
            'test_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Prompt testing error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Resume Processing Settings Routes


@admin_bp.route('/settings/ai', methods=['GET', 'PUT'])
@admin_required
def manage_ai_settings():
    """Manage AI-specific resume processing settings."""
    try:
        settings = ResumeProcessingSettings.query.first()

        if request.method == 'GET':
            return jsonify(settings.get_ai_settings() if settings else {})

        if request.method == 'PUT':
            data = request.get_json()

            if not settings:
                settings = ResumeProcessingSettings()
                db.session.add(settings)

            settings.update_ai_settings(data)
            settings.updated_by = request.admin.id
            settings.updated_at = datetime.utcnow()

            # Log admin activity
            activity = AdminActivity(
                admin_id=request.admin.id,
                action='update_ai_settings',
                details='Updated AI processing settings'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify(settings.get_ai_settings())

    except Exception as e:
        logger.error(f"AI settings management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/settings/matching', methods=['GET', 'PUT'])
@admin_required
def manage_matching_settings():
    """Manage resume-job matching settings."""
    try:
        settings = ResumeProcessingSettings.query.first()

        if request.method == 'GET':
            return jsonify(settings.get_matching_settings() if settings else {})

        if request.method == 'PUT':
            data = request.get_json()

            if not settings:
                settings = ResumeProcessingSettings()
                db.session.add(settings)

            settings.update_matching_settings(data)
            settings.updated_by = request.admin.id
            settings.updated_at = datetime.utcnow()

            # Log admin activity
            activity = AdminActivity(
                admin_id=request.admin.id,
                action='update_matching_settings',
                details='Updated resume-job matching settings'
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify(settings.get_matching_settings())

    except Exception as e:
        logger.error(f"Matching settings management error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Admin Activity Routes


@admin_bp.route('/activity', methods=['GET'])
@admin_required
def get_admin_activity():
    """Get admin activity logs."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        activities = AdminActivity.query\
            .order_by(AdminActivity.created_at.desc())\
            .paginate(page=page, per_page=per_page)

        return jsonify({
            'activities': [activity.to_dict() for activity in activities.items],
            'total': activities.total,
            'pages': activities.pages,
            'current_page': activities.page
        })

    except Exception as e:
        logger.error(f"Activity log error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Error Handlers


@admin_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'message': 'Resource not found'}), 404


@admin_bp.errorhandler(400)
def bad_request_error(error):
    return jsonify({'message': 'Bad request'}), 400


@admin_bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({'message': 'Internal server error'}), 500

# API Endpoints


@admin_bp.route('/api/stats', methods=['GET'])
@admin_required
def get_stats():
    """Get dashboard statistics."""
    try:
        stats = {
            'users': Admin.query.count(),
            'resumes': Resume.query.count(),
            'categories': JobCategory.query.count(),
            'prompts': AIPrompt.query.count()
        }
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/job-categories', methods=['GET'])
@admin_required
def get_job_categories():
    """Get all job categories."""
    try:
        categories = JobCategory.query.all()
        current_app.logger.info(
            f"Found {len(categories)} job categories in the database")

        result = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'is_active': category.is_active,
                'created_at': category.created_at.isoformat() if category.created_at else None,
                'updated_at': category.updated_at.isoformat() if category.updated_at else None
            }
            result.append(category_data)
            current_app.logger.info(
                f"Added category to result: {category.name}")

        current_app.logger.info(f"Returning {len(result)} job categories")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting job categories: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/job-categories/<int:category_id>', methods=['GET'])
@admin_required
def get_job_category(category_id):
    """Get a specific job category."""
    try:
        category = JobCategory.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404

        result = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'status': 'active' if category.is_active else 'inactive',
            'created_at': category.created_at.isoformat() if category.created_at else None,
            'updated_at': category.updated_at.isoformat() if category.updated_at else None
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting job category: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/job-categories', methods=['POST'])
@admin_required
def create_job_category():
    """Create a new job category."""
    try:
        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'message': 'Name is required'}), 400

        # Check if category with same name already exists
        existing = JobCategory.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'message': 'A category with this name already exists'}), 400

        category = JobCategory(
            name=data['name'],
            description=data.get('description', ''),
            is_active=data.get('status', 'active') == 'active'
        )

        db.session.add(category)
        db.session.commit()

        # Log activity
        admin_id = request.admin.id if hasattr(request, 'admin') else None
        activity = AdminActivity(
            admin_id=admin_id,
            action='create',
            resource='job_category',
            resource_id=category.id,
            details=f"Created job category: {category.name}"
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'Job category created successfully',
            'id': category.id
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating job category: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/job-categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_job_category(category_id):
    """Update a job category."""
    try:
        category = JobCategory.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404

        data = request.get_json()

        if not data:
            return jsonify({'message': 'No data provided'}), 400

        if 'name' in data and data['name'] != category.name:
            # Check if another category with this name exists
            existing = JobCategory.query.filter_by(name=data['name']).first()
            if existing and existing.id != category_id:
                return jsonify({'message': 'A category with this name already exists'}), 400
            category.name = data['name']

        if 'description' in data:
            category.description = data['description']

        if 'status' in data:
            category.is_active = data['status'] == 'active'

        category.updated_at = datetime.utcnow()
        db.session.commit()

        # Log activity
        admin_id = request.admin.id if hasattr(request, 'admin') else None
        activity = AdminActivity(
            admin_id=admin_id,
            action='update',
            resource='job_category',
            resource_id=category.id,
            details=f"Updated job category: {category.name}"
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'Job category updated successfully',
            'id': category.id
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating job category: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/job-categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_job_category(category_id):
    """Delete a job category."""
    try:
        category = JobCategory.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404

        # Check if category is in use
        prompts = AIPrompt.query.filter_by(category_id=category_id).count()
        if prompts > 0:
            return jsonify({
                'message': f'Cannot delete category. It is used by {prompts} prompts.'
            }), 400

        category_name = category.name
        db.session.delete(category)

        # Log activity
        admin_id = request.admin.id if hasattr(request, 'admin') else None
        activity = AdminActivity(
            admin_id=admin_id,
            action='delete',
            resource='job_category',
            resource_id=category_id,
            details=f"Deleted job category: {category_name}"
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'Job category deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job category: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/prompts', methods=['GET'])
@admin_required
def get_prompts():
    """Get all AI prompts."""
    try:
        prompts = AIPrompt.query.all()
        current_app.logger.info(
            f"Found {len(prompts)} prompts in the database")

        result = []
        for prompt in prompts:
            category = JobCategory.query.get(prompt.job_category_id)
            prompt_data = {
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'prompt_template': prompt.prompt_template,
                'job_type': prompt.job_type,
                'version': prompt.version,
                'is_active': prompt.is_active,
                'job_category_id': prompt.job_category_id,
                'category_name': category.name if category else 'Unknown',
                'created_at': prompt.created_at.isoformat() if prompt.created_at else None,
                'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
            }
            result.append(prompt_data)
            current_app.logger.info(f"Added prompt to result: {prompt.name}")

        current_app.logger.info(f"Returning {len(result)} prompts")
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting prompts: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/prompts/<int:prompt_id>', methods=['GET'])
@admin_required
def get_prompt(prompt_id):
    """Get a specific AI prompt."""
    try:
        prompt = AIPrompt.query.get(prompt_id)
        if not prompt:
            return jsonify({'message': 'Prompt not found'}), 404

        category = JobCategory.query.get(prompt.job_category_id)
        result = {
            'id': prompt.id,
            'name': prompt.name,
            'description': prompt.description,
            'prompt_template': prompt.prompt_template,
            'job_type': prompt.job_type,
            'version': prompt.version,
            'is_active': prompt.is_active,
            'job_category_id': prompt.job_category_id,
            'category_name': category.name if category else 'Unknown',
            'created_at': prompt.created_at.isoformat() if prompt.created_at else None,
            'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting prompt: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/prompts', methods=['POST'])
@admin_required
def create_prompt():
    """Create a new AI prompt."""
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'prompt_template' not in data or 'job_type' not in data:
            return jsonify({'message': 'Name, prompt template, and job type are required'}), 400

        # Check if category exists if provided
        if 'job_category_id' in data and data['job_category_id']:
            category = JobCategory.query.get(data['job_category_id'])
            if not category:
                return jsonify({'message': 'Category not found'}), 404

        # Check if prompt with same name already exists
        existing = AIPrompt.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({
                'message': f'A prompt with this name already exists'
            }), 400

        prompt = AIPrompt(
            name=data['name'],
            description=data.get('description', ''),
            prompt_template=data['prompt_template'],
            job_type=data['job_type'],
            version=data.get('version', '1.0'),
            job_category_id=data.get('job_category_id'),
            admin_id=request.admin.id if hasattr(request, 'admin') else 1
        )

        db.session.add(prompt)
        db.session.commit()

        # Log activity
        admin_id = request.admin.id if hasattr(request, 'admin') else None
        category_name = category.name if 'category' in locals() and category else 'None'
        activity = AdminActivity(
            admin_id=admin_id,
            action='create',
            resource='ai_prompt',
            resource_id=prompt.id,
            details=f"Created AI prompt: {prompt.name} for {category_name}"
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'AI prompt created successfully',
            'id': prompt.id
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating prompt: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/prompts/<int:prompt_id>', methods=['PUT'])
@admin_required
def update_prompt(prompt_id):
    """Update an AI prompt."""
    try:
        prompt = AIPrompt.query.get(prompt_id)
        if not prompt:
            return jsonify({'message': 'Prompt not found'}), 404

        data = request.get_json()

        if not data:
            return jsonify({'message': 'No data provided'}), 400

        # Update fields if provided
        if 'name' in data:
            # Check if another prompt with this name exists
            existing = AIPrompt.query.filter_by(name=data['name']).first()
            if existing and existing.id != prompt_id:
                return jsonify({'message': 'A prompt with this name already exists'}), 400
            prompt.name = data['name']

        if 'description' in data:
            prompt.description = data['description']

        if 'prompt_template' in data:
            prompt.prompt_template = data['prompt_template']

        if 'job_type' in data:
            prompt.job_type = data['job_type']

        if 'version' in data:
            prompt.version = data['version']

        if 'job_category_id' in data:
            # Check if category exists
            if data['job_category_id']:
                category = JobCategory.query.get(data['job_category_id'])
                if not category:
                    return jsonify({'message': 'Category not found'}), 404
            prompt.job_category_id = data['job_category_id']

        prompt.updated_at = datetime.utcnow()
        db.session.commit()

        # Log activity
        admin_id = request.admin.id if hasattr(request, 'admin') else None
        category = JobCategory.query.get(
            prompt.job_category_id) if prompt.job_category_id else None
        activity = AdminActivity(
            admin_id=admin_id,
            action='update',
            resource='ai_prompt',
            resource_id=prompt.id,
            details=f"Updated AI prompt: {prompt.name} for {category.name if category else 'None'}"
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'AI prompt updated successfully',
            'id': prompt.id
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating prompt: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@admin_bp.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
@admin_required
def delete_prompt(prompt_id):
    """Delete an AI prompt."""
    try:
        prompt = AIPrompt.query.get(prompt_id)
        if not prompt:
            return jsonify({'message': 'Prompt not found'}), 404

        prompt_name = prompt.name
        category = JobCategory.query.get(
            prompt.job_category_id) if prompt.job_category_id else None
        category_name = category.name if category else 'None'

        db.session.delete(prompt)

        # Log activity
        admin_id = request.admin.id if hasattr(request, 'admin') else None
        activity = AdminActivity(
            admin_id=admin_id,
            action='delete',
            resource='ai_prompt',
            resource_id=prompt_id,
            details=f"Deleted AI prompt: {prompt_name} for {category_name}"
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'AI prompt deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting prompt: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Resume Management Routes


@admin_bp.route('/api/resumes', methods=['GET'])
@admin_required
def get_resumes():
    """Get all resumes with optional filtering."""
    try:
        # Get query parameters for filtering
        job_category = request.args.get('job_category')
        status = request.args.get('status')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        # Default sort by upload date
        sort_by = request.args.get('sort_by', 'upload_date')
        sort_order = request.args.get(
            'sort_order', 'desc')  # Default descending order

        # Build query
        query = Resume.query.outerjoin(
            ProcessedResume, Resume.id == ProcessedResume.resume_id)

        # Apply filters if provided
        if job_category:
            query = query.join(JobPosting).filter(
                JobPosting.category_id == job_category)

        if status:
            query = query.filter(Resume.status == status)

        # Filter by ranking score if provided
        if min_score is not None:
            query = query.filter(ProcessedResume.ranking_score >= min_score)

        if max_score is not None:
            query = query.filter(ProcessedResume.ranking_score <= max_score)

        # Apply sorting
        if sort_by == 'ranking_score':
            if sort_order == 'desc':
                query = query.order_by(ProcessedResume.ranking_score.desc())
            else:
                query = query.order_by(ProcessedResume.ranking_score.asc())
        elif sort_by == 'upload_date':
            if sort_order == 'desc':
                query = query.order_by(Resume.upload_date.desc())
            else:
                query = query.order_by(Resume.upload_date.asc())
        elif sort_by == 'job_role':
            if sort_order == 'desc':
                query = query.order_by(Resume.job_role.desc())
            else:
                query = query.order_by(Resume.job_role.asc())

        # Execute query
        resumes = query.all()

        # Convert to dict and include processed data if available
        result = []
        for resume in resumes:
            resume_dict = {
                'id': resume.id,
                'filename': resume.filename,
                'original_filename': resume.original_filename,
                'job_role': resume.job_role,
                'upload_date': resume.upload_date.isoformat() if resume.upload_date else None,
                'status': resume.status,
                'candidate_name': resume.candidate_name,
                'candidate_email': resume.candidate_email,
                'admin_feedback': resume.admin_feedback,
                'pdf_report_path': resume.pdf_report_path
            }

            # Add processed data if available
            if resume.processed_resume:
                # Keep decimal precision for ranking scores
                resume_dict['ranking_score'] = float(
                    resume.processed_resume.ranking_score) if resume.processed_resume.ranking_score is not None else None
                resume_dict['skills_match'] = resume.processed_resume.skills_match
                resume_dict['experience_match'] = float(
                    resume.processed_resume.experience_match) if resume.processed_resume.experience_match is not None else None
                resume_dict['education_match'] = float(
                    resume.processed_resume.education_match) if resume.processed_resume.education_match is not None else None
                resume_dict['overall_ranking'] = resume.processed_resume.overall_ranking

            result.append(resume_dict)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting resumes: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/api/resumes/<int:resume_id>', methods=['GET'])
@admin_required
def get_resume(resume_id):
    """Get a specific resume by ID."""
    try:
        resume = Resume.query.get_or_404(resume_id)

        # Build response
        result = {
            'id': resume.id,
            'filename': resume.filename,
            'original_filename': resume.original_filename,
            'job_role': resume.job_role,
            'file_path': resume.file_path,
            'upload_date': resume.upload_date.isoformat() if resume.upload_date else None,
            'status': resume.status,
            'candidate_name': resume.candidate_name,
            'candidate_email': resume.candidate_email,
            'admin_feedback': resume.admin_feedback,
            'pdf_report_path': resume.pdf_report_path
        }

        # Add processed data if available
        if resume.processed_resume:
            result['processed_data'] = resume.processed_resume.processed_data
            result['ranking_score'] = resume.processed_resume.ranking_score
            result['skills_match'] = resume.processed_resume.skills_match
            result['experience_match'] = resume.processed_resume.experience_match
            result['education_match'] = resume.processed_resume.education_match
            result['overall_ranking'] = resume.processed_resume.overall_ranking
            result['feedback'] = resume.processed_resume.feedback

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting resume {resume_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/api/resumes/<int:resume_id>/status', methods=['PUT'])
@admin_required
def update_resume_status(resume_id):
    """Update resume status."""
    try:
        resume = Resume.query.get_or_404(resume_id)
        data = request.get_json()

        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400

        # Validate status
        valid_statuses = ['pending', 'processing',
                          'processed', 'approved', 'rejected', 'shortlisted']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

        # Update status
        resume.status = data['status']

        # Log admin activity
        activity = AdminActivity(
            admin_id=request.admin.id,
            action=f'update_resume_status_{data["status"]}',
            resource='resume',
            resource_id=resume.id,
            details=f'Updated resume status to {data["status"]}'
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': f'Resume status updated to {data["status"]}', 'status': data['status']})

    except Exception as e:
        logger.error(f"Error updating resume status {resume_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/api/resumes/<int:resume_id>/feedback', methods=['PUT'])
@admin_required
def update_resume_feedback(resume_id):
    """Update admin feedback for a resume."""
    try:
        resume = Resume.query.get_or_404(resume_id)
        data = request.get_json()

        if 'feedback' not in data:
            return jsonify({'error': 'Feedback is required'}), 400

        # Update feedback
        resume.admin_feedback = data['feedback']

        # Log admin activity
        activity = AdminActivity(
            admin_id=request.admin.id,
            action='update_resume_feedback',
            resource='resume',
            resource_id=resume.id,
            details='Updated resume feedback'
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Resume feedback updated', 'feedback': data['feedback']})

    except Exception as e:
        logger.error(f"Error updating resume feedback {resume_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/resumes/<int:resume_id>', methods=['GET'])
@admin_required
def view_resume(resume_id):
    """View resume details page."""
    try:
        # Get the resume with all related data in a single query
        resume = Resume.query.options(
            db.joinedload(Resume.job_posting).joinedload(JobPosting.category),
            db.joinedload(Resume.processed_resume)
        ).get_or_404(resume_id)

        # Get job posting if available
        job_posting = resume.job_posting

        # Render template
        return render_template(
            'admin_resume_view.html',
            resume=resume,
            job_posting=job_posting,
            admin=request.admin
        )

    except Exception as e:
        logger.error(f"Error viewing resume {resume_id}: {str(e)}")
        return render_template('error.html', error=str(e))

# Resume Dashboard


@admin_bp.route('/resumes', methods=['GET'])
@admin_required
def resume_dashboard():
    """Resume management dashboard."""
    try:
        # Get filter parameters
        job_role = request.args.get('job_role')
        status = request.args.get('status')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        sort_by = request.args.get('sort_by', 'upload_date')
        sort_order = request.args.get('sort_order', 'desc')

        # Get job categories for filter
        job_categories = JobCategory.query.filter_by(is_active=True).all()

        # Get unique job roles for filter
        job_roles = db.session.query(
            Resume.job_role).distinct().order_by(Resume.job_role).all()
        # Extract role names and filter out None values
        job_roles = [role[0] for role in job_roles if role[0]]

        # Get resume statuses for filter
        statuses = [
            {'value': 'pending', 'label': 'Pending'},
            {'value': 'processing', 'label': 'Processing'},
            {'value': 'processed', 'label': 'Processed'},
            {'value': 'approved', 'label': 'Approved'},
            {'value': 'rejected', 'label': 'Rejected'},
            {'value': 'shortlisted', 'label': 'Shortlisted'}
        ]

        # Build query with filters
        query = Resume.query

        # Apply job role filter if provided
        if job_role:
            query = query.filter(Resume.job_role == job_role)

        # Apply status filter if provided
        if status:
            query = query.filter(Resume.status == status)

        # Define an alias for ProcessedResume to avoid ambiguity
        pr_alias = db.aliased(ProcessedResume)

        # Join with ProcessedResume for score filtering and sorting if needed
        if min_score is not None or max_score is not None or sort_by == 'ranking_score':
            query = query.outerjoin(pr_alias, Resume.id == pr_alias.resume_id)

            # Apply min score filter if provided
            if min_score is not None:
                query = query.filter(pr_alias.ranking_score >= min_score)

            # Apply max score filter if provided
            if max_score is not None:
                query = query.filter(pr_alias.ranking_score <= max_score)

        # Get resume stats (always show total counts regardless of filters)
        stats = {
            'total': Resume.query.count(),
            'pending': Resume.query.filter_by(status='pending').count(),
            'processing': Resume.query.filter_by(status='processing').count(),
            'processed': Resume.query.filter_by(status='processed').count(),
            'approved': Resume.query.filter_by(status='approved').count(),
            'rejected': Resume.query.filter_by(status='rejected').count(),
            'shortlisted': Resume.query.filter_by(status='shortlisted').count()
        }

        # Apply sorting
        if sort_by == 'ranking_score':
            # Simplified sorting to avoid errors
            if sort_order == 'asc':
                query = query.order_by(
                    pr_alias.ranking_score.asc().nullslast())
            else:
                query = query.order_by(
                    pr_alias.ranking_score.desc().nullslast())
        elif sort_by == 'job_role':
            # Sort by job_role directly
            if sort_order == 'asc':
                query = query.order_by(Resume.job_role.asc())
            else:
                query = query.order_by(Resume.job_role.desc())
        else:  # Default to upload_date
            if sort_order == 'asc':
                query = query.order_by(Resume.upload_date.asc())
            else:
                query = query.order_by(Resume.upload_date.desc())

        # Get all resumes with job posting and category information
        resumes = query.options(
            db.joinedload(Resume.job_posting).joinedload(JobPosting.category),
            db.joinedload(Resume.processed_resume)
        ).all()

        # Debug information
        print(
            f"Filter params: job_role={job_role}, status={status}, min_score={min_score}, max_score={max_score}")
        print(f"Sort params: sort_by={sort_by}, sort_order={sort_order}")
        print(f"Found {len(resumes)} resumes matching criteria")

        return render_template(
            'admin_resume_dashboard.html',
            job_categories=job_categories,
            job_roles=job_roles,
            statuses=statuses,
            stats=stats,
            resumes=resumes,
            admin=request.admin,
            request=request  # Pass request to template for accessing args
        )

    except Exception as e:
        logger.error(f"Error loading resume dashboard: {str(e)}")
        return render_template('error.html', error=str(e))

# Job Category Management Page


@admin_bp.route('/job-categories', methods=['GET'])
@admin_required
def job_categories_page():
    """Job category management page."""
    try:
        # Fetch all job categories from database
        job_categories = JobCategory.query.all()
        logger.info(f"Loaded {len(job_categories)} job categories for display")

        return render_template(
            'admin_job_categories.html',
            admin=request.admin,
            job_categories=job_categories
        )
    except Exception as e:
        logger.error(f"Error loading job categories page: {str(e)}")
        return render_template('error.html', error=str(e))

# AI Prompt Management Page


@admin_bp.route('/prompts-management', methods=['GET'])
@admin_required
def prompts_management_page():
    """AI prompt management page."""
    try:
        # Fetch all AI prompts from database
        prompts = AIPrompt.query.all()
        logger.info(f"Loaded {len(prompts)} AI prompts for display")

        return render_template(
            'admin_prompts.html',
            admin=request.admin,
            prompts=prompts
        )
    except Exception as e:
        logger.error(f"Error loading prompts page: {str(e)}")
        return render_template('error.html', error=str(e))


@admin_bp.route('/api/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        # Get counts
        resume_count = Resume.query.count()
        processed_resume_count = Resume.query.filter(
            Resume.status == 'processed').count()
        job_category_count = JobCategory.query.count()
        ai_prompt_count = AIPrompt.query.count()
        admin_count = Admin.query.count()

        return jsonify({
            'resume_count': resume_count,
            'processed_resume_count': processed_resume_count,
            'job_category_count': job_category_count,
            'ai_prompt_count': ai_prompt_count,
            'admin_count': admin_count
        })

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@admin_bp.route('/logout', methods=['GET'])
def logout():
    """Logout admin user."""
    try:
        # Clear cookies
        response = redirect(url_for('admin.login'))
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return redirect(url_for('admin.login'))


@admin_bp.route('/resumes/<int:resume_id>/reprocess', methods=['POST'])
@admin_required
def reprocess_resume(resume_id):
    """Reprocess a resume with AI analysis."""
    try:
        # Get the resume
        resume = Resume.query.get_or_404(resume_id)

        # Get the AI service
        ai_service = AIService()

        # Extract text content from the file
        resume_processor = ResumeProcessor()
        text_content = resume_processor.extract_text_from_file(
            resume.file_path, resume.mime_type)

        # Process the resume
        if resume.job_id:
            processed_data, ranking_score = ai_service.process_resume_with_job(
                text_content, resume.job_role, resume.job_id)
        else:
            processed_data, ranking_score = ai_service.process_resume(
                text_content, resume.job_role)

        # Update or create processed resume record
        processed_resume = ProcessedResume.query.filter_by(
            resume_id=resume.id).first()

        if processed_resume:
            # Update existing record
            processed_resume.processed_data = processed_data
            processed_resume.ranking_score = ranking_score
            processed_resume.skills_match = processed_data.get('skills_match')
            processed_resume.experience_match = processed_data.get(
                'experience_relevance', 0)
            processed_resume.education_match = processed_data.get(
                'education_relevance', 0)
            processed_resume.feedback = processed_data
        else:
            # Create new record
            processed_resume = ProcessedResume(
                resume_id=resume.id,
                processed_data=processed_data,
                ranking_score=ranking_score,
                skills_match=processed_data.get('skills_match'),
                experience_match=processed_data.get('experience_relevance', 0),
                education_match=processed_data.get('education_relevance', 0),
                feedback=processed_data
            )
            db.session.add(processed_resume)

        # Update resume status
        resume.status = 'processed'
        db.session.commit()

        return jsonify({'success': True, 'message': 'Resume reprocessed successfully'})

    except Exception as e:
        current_app.logger.error(f"Error reprocessing resume: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/resumes/approved', methods=['GET'])
@admin_required
def approved_resumes():
    """Approved resumes dashboard."""
    try:
        # Get filter parameters
        job_role = request.args.get('job_role')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        sort_by = request.args.get('sort_by', 'upload_date')
        sort_order = request.args.get('sort_order', 'desc')

        # Get job categories for filter
        job_categories = JobCategory.query.filter_by(is_active=True).all()

        # Get unique job roles for filter
        job_roles = db.session.query(
            Resume.job_role).distinct().order_by(Resume.job_role).all()
        # Extract role names and filter out None values
        job_roles = [role[0] for role in job_roles if role[0]]

        # Get resume statuses for filter
        statuses = [
            {'value': 'pending', 'label': 'Pending'},
            {'value': 'processing', 'label': 'Processing'},
            {'value': 'processed', 'label': 'Processed'},
            {'value': 'approved', 'label': 'Approved'},
            {'value': 'rejected', 'label': 'Rejected'},
            {'value': 'shortlisted', 'label': 'Shortlisted'}
        ]

        # Build query with filters - always filter by approved status
        query = Resume.query.filter(Resume.status == 'approved')

        # Apply job role filter if provided
        if job_role:
            query = query.filter(Resume.job_role == job_role)

        # Define an alias for ProcessedResume to avoid ambiguity
        pr_alias = db.aliased(ProcessedResume)

        # Join with ProcessedResume for score filtering and sorting if needed
        if min_score is not None or max_score is not None or sort_by == 'ranking_score':
            query = query.outerjoin(pr_alias, Resume.id == pr_alias.resume_id)

            # Apply min score filter if provided
            if min_score is not None:
                query = query.filter(pr_alias.ranking_score >= min_score)

            # Apply max score filter if provided
            if max_score is not None:
                query = query.filter(pr_alias.ranking_score <= max_score)

        # Get resume stats (always show total counts regardless of filters)
        stats = {
            'total': Resume.query.count(),
            'pending': Resume.query.filter_by(status='pending').count(),
            'processing': Resume.query.filter_by(status='processing').count(),
            'processed': Resume.query.filter_by(status='processed').count(),
            'approved': Resume.query.filter_by(status='approved').count(),
            'rejected': Resume.query.filter_by(status='rejected').count(),
            'shortlisted': Resume.query.filter_by(status='shortlisted').count()
        }

        # Apply sorting
        if sort_by == 'ranking_score':
            # Simplified sorting to avoid errors
            if sort_order == 'asc':
                query = query.order_by(
                    pr_alias.ranking_score.asc().nullslast())
            else:
                query = query.order_by(
                    pr_alias.ranking_score.desc().nullslast())
        elif sort_by == 'job_role':
            # Sort by job_role directly
            if sort_order == 'asc':
                query = query.order_by(Resume.job_role.asc())
            else:
                query = query.order_by(Resume.job_role.desc())
        else:  # Default to upload_date
            if sort_order == 'asc':
                query = query.order_by(Resume.upload_date.asc())
            else:
                query = query.order_by(Resume.upload_date.desc())

        # Get all resumes with job posting and category information
        resumes = query.options(
            db.joinedload(Resume.job_posting).joinedload(JobPosting.category),
            db.joinedload(Resume.processed_resume)
        ).all()

        # Debug information
        print(
            f"Filter params: job_role={job_role}, status=approved, min_score={min_score}, max_score={max_score}")
        print(f"Sort params: sort_by={sort_by}, sort_order={sort_order}")
        print(f"Found {len(resumes)} approved resumes matching criteria")

        return render_template(
            'admin_approved_resumes.html',
            job_categories=job_categories,
            job_roles=job_roles,
            statuses=statuses,
            stats=stats,
            resumes=resumes,
            admin=request.admin,
            request=request,  # Pass request to template for accessing args
            page_title="Approved Resumes"
        )
    except Exception as e:
        logger.error(f"Error loading approved resumes dashboard: {str(e)}")
        return render_template('error.html', error=str(e))


@admin_bp.route('/resumes/rejected', methods=['GET'])
@admin_required
def rejected_resumes():
    """Rejected resumes dashboard."""
    try:
        # Get filter parameters
        job_role = request.args.get('job_role')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        sort_by = request.args.get('sort_by', 'upload_date')
        sort_order = request.args.get('sort_order', 'desc')

        # Get job categories for filter
        job_categories = JobCategory.query.filter_by(is_active=True).all()

        # Get unique job roles for filter
        job_roles = db.session.query(
            Resume.job_role).distinct().order_by(Resume.job_role).all()
        # Extract role names and filter out None values
        job_roles = [role[0] for role in job_roles if role[0]]

        # Get resume statuses for filter
        statuses = [
            {'value': 'pending', 'label': 'Pending'},
            {'value': 'processing', 'label': 'Processing'},
            {'value': 'processed', 'label': 'Processed'},
            {'value': 'approved', 'label': 'Approved'},
            {'value': 'rejected', 'label': 'Rejected'},
            {'value': 'shortlisted', 'label': 'Shortlisted'}
        ]

        # Build query with filters - always filter by rejected status
        query = Resume.query.filter(Resume.status == 'rejected')

        # Apply job role filter if provided
        if job_role:
            query = query.filter(Resume.job_role == job_role)

        # Define an alias for ProcessedResume to avoid ambiguity
        pr_alias = db.aliased(ProcessedResume)

        # Join with ProcessedResume for score filtering and sorting if needed
        if min_score is not None or max_score is not None or sort_by == 'ranking_score':
            query = query.outerjoin(pr_alias, Resume.id == pr_alias.resume_id)

            # Apply min score filter if provided
            if min_score is not None:
                query = query.filter(pr_alias.ranking_score >= min_score)

            # Apply max score filter if provided
            if max_score is not None:
                query = query.filter(pr_alias.ranking_score <= max_score)

        # Get resume stats (always show total counts regardless of filters)
        stats = {
            'total': Resume.query.count(),
            'pending': Resume.query.filter_by(status='pending').count(),
            'processing': Resume.query.filter_by(status='processing').count(),
            'processed': Resume.query.filter_by(status='processed').count(),
            'approved': Resume.query.filter_by(status='approved').count(),
            'rejected': Resume.query.filter_by(status='rejected').count(),
            'shortlisted': Resume.query.filter_by(status='shortlisted').count()
        }

        # Apply sorting
        if sort_by == 'ranking_score':
            # Simplified sorting to avoid errors
            if sort_order == 'asc':
                query = query.order_by(
                    pr_alias.ranking_score.asc().nullslast())
            else:
                query = query.order_by(
                    pr_alias.ranking_score.desc().nullslast())
        elif sort_by == 'job_role':
            # Sort by job_role directly
            if sort_order == 'asc':
                query = query.order_by(Resume.job_role.asc())
            else:
                query = query.order_by(Resume.job_role.desc())
        else:  # Default to upload_date
            if sort_order == 'asc':
                query = query.order_by(Resume.upload_date.asc())
            else:
                query = query.order_by(Resume.upload_date.desc())

        # Get all resumes with job posting and category information
        resumes = query.options(
            db.joinedload(Resume.job_posting).joinedload(JobPosting.category),
            db.joinedload(Resume.processed_resume)
        ).all()

        # Debug information
        print(
            f"Filter params: job_role={job_role}, status=rejected, min_score={min_score}, max_score={max_score}")
        print(f"Sort params: sort_by={sort_by}, sort_order={sort_order}")
        print(f"Found {len(resumes)} rejected resumes matching criteria")

        return render_template(
            'admin_rejected_resumes.html',
            job_categories=job_categories,
            job_roles=job_roles,
            statuses=statuses,
            stats=stats,
            resumes=resumes,
            admin=request.admin,
            request=request,  # Pass request to template for accessing args
            page_title="Rejected Resumes"
        )
    except Exception as e:
        logger.error(f"Error loading rejected resumes dashboard: {str(e)}")
        return render_template('error.html', error=str(e))


@admin_bp.route('/resumes/shortlisted', methods=['GET'])
@admin_required
def shortlisted_resumes():
    """Shortlisted resumes dashboard."""
    try:
        # Get filter parameters
        job_role = request.args.get('job_role')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        sort_by = request.args.get('sort_by', 'upload_date')
        sort_order = request.args.get('sort_order', 'desc')

        # Get job categories for filter
        job_categories = JobCategory.query.filter_by(is_active=True).all()

        # Get unique job roles for filter
        job_roles = db.session.query(
            Resume.job_role).distinct().order_by(Resume.job_role).all()
        # Extract role names and filter out None values
        job_roles = [role[0] for role in job_roles if role[0]]

        # Get resume statuses for filter
        statuses = [
            {'value': 'pending', 'label': 'Pending'},
            {'value': 'processing', 'label': 'Processing'},
            {'value': 'processed', 'label': 'Processed'},
            {'value': 'approved', 'label': 'Approved'},
            {'value': 'rejected', 'label': 'Rejected'},
            {'value': 'shortlisted', 'label': 'Shortlisted'}
        ]

        # Build query with filters - always filter by shortlisted status
        query = Resume.query.filter(Resume.status == 'shortlisted')

        # Apply job role filter if provided
        if job_role:
            query = query.filter(Resume.job_role == job_role)

        # Define an alias for ProcessedResume to avoid ambiguity
        pr_alias = db.aliased(ProcessedResume)

        # Join with ProcessedResume for score filtering and sorting if needed
        if min_score is not None or max_score is not None or sort_by == 'ranking_score':
            query = query.outerjoin(pr_alias, Resume.id == pr_alias.resume_id)

            # Apply min score filter if provided
            if min_score is not None:
                query = query.filter(pr_alias.ranking_score >= min_score)

            # Apply max score filter if provided
            if max_score is not None:
                query = query.filter(pr_alias.ranking_score <= max_score)

        # Get resume stats (always show total counts regardless of filters)
        stats = {
            'total': Resume.query.count(),
            'pending': Resume.query.filter_by(status='pending').count(),
            'processing': Resume.query.filter_by(status='processing').count(),
            'processed': Resume.query.filter_by(status='processed').count(),
            'approved': Resume.query.filter_by(status='approved').count(),
            'rejected': Resume.query.filter_by(status='rejected').count(),
            'shortlisted': Resume.query.filter_by(status='shortlisted').count()
        }

        # Apply sorting
        if sort_by == 'ranking_score':
            # Simplified sorting to avoid errors
            if sort_order == 'asc':
                query = query.order_by(
                    pr_alias.ranking_score.asc().nullslast())
            else:
                query = query.order_by(
                    pr_alias.ranking_score.desc().nullslast())
        elif sort_by == 'job_role':
            # Sort by job_role directly
            if sort_order == 'asc':
                query = query.order_by(Resume.job_role.asc())
            else:
                query = query.order_by(Resume.job_role.desc())
        else:  # Default to upload_date
            if sort_order == 'asc':
                query = query.order_by(Resume.upload_date.asc())
            else:
                query = query.order_by(Resume.upload_date.desc())

        # Get all resumes with job posting and category information
        resumes = query.options(
            db.joinedload(Resume.job_posting).joinedload(JobPosting.category),
            db.joinedload(Resume.processed_resume)
        ).all()

        # Debug information
        print(
            f"Filter params: job_role={job_role}, status=shortlisted, min_score={min_score}, max_score={max_score}")
        print(f"Sort params: sort_by={sort_by}, sort_order={sort_order}")
        print(f"Found {len(resumes)} shortlisted resumes matching criteria")

        return render_template(
            'admin_shortlisted_resumes.html',
            job_categories=job_categories,
            job_roles=job_roles,
            statuses=statuses,
            stats=stats,
            resumes=resumes,
            admin=request.admin,
            request=request,  # Pass request to template for accessing args
            page_title="Shortlisted Resumes"
        )
    except Exception as e:
        logger.error(f"Error loading shortlisted resumes dashboard: {str(e)}")
        return render_template('error.html', error=str(e))
