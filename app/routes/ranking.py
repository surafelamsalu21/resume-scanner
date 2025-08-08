from flask import Blueprint, request, jsonify, current_app
from database.db import db
from app.models import Resume, ProcessedResume, JobPosting, RankingCriteria
from sqlalchemy import desc
from typing import List, Dict, Any
from app.services import RankingService

ranking_bp = Blueprint('ranking', __name__)


@ranking_bp.route('/job/<int:job_id>', methods=['GET'])
def get_rankings(job_id):
    """Get rankings for a specific job posting."""
    try:
        ranking_service = RankingService()
        ranked_candidates = ranking_service.rank_candidates(job_id)

        return jsonify({
            'job_id': job_id,
            'candidates': [
                {
                    'resume_id': candidate.resume.id,
                    'ranking': candidate.overall_ranking,
                    'score': candidate.ranking_score,
                    'candidate_name': candidate.resume.candidate_name,
                    'processed_data': candidate.processed_data
                }
                for candidate in ranked_candidates
            ]
        })

    except Exception as e:
        current_app.logger.error(f"Error retrieving rankings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ranking_bp.route('/alternative-roles/<int:resume_id>', methods=['GET'])
def get_alternative_roles(resume_id):
    """Get alternative role suggestions for a candidate."""
    try:
        processed_resume = ProcessedResume.query.filter_by(
            resume_id=resume_id).first()
        if not processed_resume:
            return jsonify({'error': 'Resume not found'}), 404

        ranking_service = RankingService()
        alternative_roles = ranking_service.suggest_alternative_roles(
            processed_resume.processed_data
        )

        return jsonify({
            'resume_id': resume_id,
            'alternative_roles': alternative_roles
        })

    except Exception as e:
        current_app.logger.error(f"Error finding alternative roles: {str(e)}")
        return jsonify({'error': str(e)}), 500


@ranking_bp.route('/batch-compare', methods=['POST'])
def batch_compare():
    """Compare multiple resumes for a job posting."""
    try:
        data = request.get_json()
        if not data or 'resume_ids' not in data or 'job_id' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        resume_ids = data['resume_ids']
        job_id = data['job_id']

        # Get job posting
        job_posting = JobPosting.query.get(job_id)
        if not job_posting:
            return jsonify({'error': 'Job posting not found'}), 404

        # Get processed resumes
        processed_resumes = ProcessedResume.query.filter(
            ProcessedResume.resume_id.in_(resume_ids)
        ).all()

        # Compare resumes
        comparison_results = []
        for processed_resume in processed_resumes:
            comparison_results.append({
                'resume_id': processed_resume.resume_id,
                'candidate_name': processed_resume.resume.candidate_name,
                'ranking_score': processed_resume.ranking_score,
                'skills_match': processed_resume.skills_match,
                'experience_match': processed_resume.experience_match,
                'education_match': processed_resume.education_match,
                'overall_ranking': processed_resume.overall_ranking
            })

        # Sort by ranking score
        comparison_results.sort(key=lambda x: x['ranking_score'], reverse=True)

        return jsonify({
            'job_id': job_id,
            'job_title': job_posting.title,
            'comparison_results': comparison_results
        })

    except Exception as e:
        current_app.logger.error(f"Error in batch comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500
