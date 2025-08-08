from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from database.db import db
from app.models import Resume, ProcessedResume, JobPosting, JobCategory
from app.services import ResumeProcessor, AIService
import magic

resume_bp = Blueprint('resume', __name__)

# File upload configuration
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
ALLOWED_MIME_TYPES = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'text/plain': 'txt'
}


def allowed_file(filename, mime_type):
    """Check if file is allowed based on extension and MIME type."""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and
            mime_type in ALLOWED_MIME_TYPES)


@resume_bp.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    """Handle resume upload and processing."""
    # For GET requests, render the upload form
    if request.method == 'GET':
        # Get available job roles for the dropdown - only get active job categories
        job_categories = JobCategory.query.filter_by(is_active=True).all()

        return render_template('upload.html',
                               job_categories=job_categories)

    # For POST requests, process the uploaded file
    try:
        current_app.logger.info("Processing resume upload request")

        if 'file' not in request.files:
            current_app.logger.error("No file provided in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        job_role = request.form.get('job_role')

        # Validate job role - ensure it's one of our specific job roles
        if not job_role:
            current_app.logger.error("No job role provided")
            return jsonify({'error': 'Please select a job role'}), 400

        # Check if the job role exists in our categories
        job_category = JobCategory.query.filter_by(name=job_role).first()
        if not job_category:
            current_app.logger.error(f"Invalid job role: {job_role}")
            return jsonify({'error': 'Please select a valid job role'}), 400

        # We're not using job_id anymore
        candidate_name = request.form.get('candidate_name', '')
        candidate_email = request.form.get('candidate_email', '')

        current_app.logger.info(
            f"File: {file.filename}, Job Role: {job_role}")

        if file.filename == '':
            current_app.logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400

        # Check file type using python-magic
        file_bytes = file.read()
        file.seek(0)  # Reset file pointer after reading
        mime_type = magic.from_buffer(file_bytes, mime=True)

        if not allowed_file(file.filename, mime_type):
            current_app.logger.error(
                f"Invalid file type: {mime_type} for file {file.filename}")
            return jsonify({'error': 'Invalid file type. Please upload a PDF, DOCX, or TXT file.'}), 400

        # Create a unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], unique_filename)

        # Save the file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        current_app.logger.info(f"File saved to {file_path}")

        # Extract text from the file
        resume_processor = ResumeProcessor()
        text_content = resume_processor.extract_text_from_file(
            file_path, mime_type)

        # Create resume record
        resume = Resume(
            filename=unique_filename,
            original_filename=filename,
            job_role=job_role,
            file_path=file_path,
            status='processing',
            candidate_name=candidate_name,
            candidate_email=candidate_email
        )
        db.session.add(resume)
        db.session.commit()

        current_app.logger.info(f"Resume record created with ID: {resume.id}")

        # Process the resume immediately instead of setting it to 'processing'
        try:
            # Analyze resume with AI - without job_id
            ai_service = AIService()
            processed_data, ranking_score = ai_service.process_resume(
                text_content, job_role)

            # Create processed resume record
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

            # Extract candidate name and email if not provided
            if not resume.candidate_name and 'candidate_name' in processed_data:
                resume.candidate_name = processed_data['candidate_name']

            if not resume.candidate_email and 'contact_info' in processed_data and 'email' in processed_data['contact_info']:
                resume.candidate_email = processed_data['contact_info']['email']

            db.session.commit()

            current_app.logger.info(
                f"Resume {resume.id} processed successfully")

        except Exception as e:
            current_app.logger.error(f"Error processing resume: {str(e)}")
            resume.status = 'error'
            db.session.commit()
            # Continue with the response even if processing failed

        # Return success response with confirmation message
        return jsonify({
            'message': 'Resume uploaded successfully! We\'ll analyze it and provide feedback.',
            'resume_id': resume.id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in resume upload: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/results/<int:resume_id>', methods=['GET'])
def get_results(resume_id):
    """Get processed results for a specific resume."""
    try:
        processed_resume = ProcessedResume.query.filter_by(
            resume_id=resume_id).first()
        if not processed_resume:
            return jsonify({'error': 'Resume not found'}), 404

        # Check if the request wants JSON response
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'processed_data': processed_resume.processed_data,
                'ranking_score': processed_resume.ranking_score,
                'job_role': processed_resume.resume.job_role
            })

        # Otherwise, render the results page
        return render_template('results.html',
                               processed_data=processed_resume.processed_data,
                               ranking_score=processed_resume.ranking_score,
                               job_role=processed_resume.resume.job_role)

    except Exception as e:
        current_app.logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get available job postings for resume upload."""
    try:
        jobs = JobPosting.query.filter_by(status='active').all()
        return jsonify([{
            'id': job.id,
            'title': job.title,
            'department': job.department
        } for job in jobs])
    except Exception as e:
        current_app.logger.error(f"Error retrieving jobs: {str(e)}")
        return jsonify({'error': str(e)}), 500
