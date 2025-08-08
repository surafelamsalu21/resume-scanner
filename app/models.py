from database.db import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app
from os import getenv
from sqlalchemy.dialects.postgresql import JSON


class Admin(db.Model):
    """Admin user model for authentication and authorization."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    job_postings = db.relationship('JobPosting', backref='admin', lazy=True)
    ai_prompts = db.relationship('AIPrompt', backref='admin', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        return jwt.encode(
            {'id': self.id, 'exp': datetime.now(
                timezone.utc) + timedelta(seconds=expires_in)},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    def generate_access_token(self):
        """Generate JWT access token for admin."""
        access_token_expires = datetime.utcnow() + timedelta(
            hours=int(getenv('JWT_ACCESS_TOKEN_EXPIRES', '1'))
        )

        return jwt.encode(
            {
                'admin_id': self.id,
                'exp': access_token_expires,
                'token_type': 'access'
            },
            getenv('JWT_SECRET_KEY', 'your_secret_key_for_jwt_tokens'),
            algorithm='HS256'
        )

    def generate_refresh_token(self):
        """Generate JWT refresh token for admin."""
        refresh_token_expires = datetime.utcnow() + timedelta(
            days=int(getenv('JWT_REFRESH_TOKEN_EXPIRES', '30'))
        )

        return jwt.encode(
            {
                'admin_id': self.id,
                'exp': refresh_token_expires,
                'token_type': 'refresh'
            },
            getenv('JWT_SECRET_KEY', 'your_secret_key_for_jwt_tokens'),
            algorithm='HS256'
        )

    def to_dict(self):
        """Convert admin object to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(
                token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return Admin.query.get(data['id'])
        except:
            return None


class JobPosting(db.Model):
    """Model for job postings with required skills and qualifications."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Structured job requirements
    requirements = db.Column(JSON, nullable=False)
    # Required qualifications
    qualifications = db.Column(JSON, nullable=False)
    skills = db.Column(JSON, nullable=False)  # Required skills with weights
    experience_level = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(16), default='active')
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    # Add foreign key to job category
    category_id = db.Column(db.Integer, db.ForeignKey(
        'job_category.id'), nullable=True)
    applications = db.relationship('Resume', backref='job_posting', lazy=True)

    def to_dict(self):
        """Convert job posting object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'department': self.department,
            'description': self.description,
            'requirements': self.requirements,
            'qualifications': self.qualifications,
            'skills': self.skills,
            'experience_level': self.experience_level,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'admin_id': self.admin_id,
            'category_id': self.category_id
        }


class AIPrompt(db.Model):
    """Model for storing and managing AI processing prompts."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    prompt_template = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(64), nullable=False)
    version = db.Column(db.String(16), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    # Add relationship to job category
    job_category_id = db.Column(
        db.Integer, db.ForeignKey('job_category.id'), nullable=True)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt_template': self.prompt_template,
            'job_type': self.job_type,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'admin_id': self.admin_id,
            'job_category_id': self.job_category_id
        }


class AIProcessingLog(db.Model):
    """Model for logging AI processing activities and performance."""
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey(
        'resume.id'), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey(
        'ai_prompt.id'), nullable=False)
    processing_start = db.Column(db.DateTime, nullable=False)
    processing_end = db.Column(db.DateTime, nullable=False)
    tokens_used = db.Column(db.Integer)
    processing_status = db.Column(db.String(16), nullable=False)
    error_message = db.Column(db.Text)
    response_data = db.Column(JSON)
    model_version = db.Column(db.String(32))
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))


class Resume(db.Model):
    """Model for storing resume information and file references."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    upload_date = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'))
    # pending, processing, processed, rejected, shortlisted, approved
    status = db.Column(db.String(16), default='pending')
    candidate_name = db.Column(db.String(128))
    candidate_email = db.Column(db.String(128))
    admin_feedback = db.Column(db.Text)
    pdf_report_path = db.Column(db.String(512))
    processed_resume = db.relationship(
        'ProcessedResume', backref='resume', uselist=False)
    processing_logs = db.relationship(
        'AIProcessingLog', backref='resume', lazy=True)


class ProcessedResume(db.Model):
    """Model for storing processed resume data and rankings."""
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey(
        'resume.id'), nullable=False)
    processed_data = db.Column(JSON, nullable=False)  # Structured resume data
    ranking_score = db.Column(db.Float, nullable=False)
    processing_date = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    skills_match = db.Column(JSON)  # Matched skills with scores
    experience_match = db.Column(db.Float)  # Experience match score
    education_match = db.Column(db.Float)  # Education match score
    overall_ranking = db.Column(db.Integer)  # Overall rank among candidates
    feedback = db.Column(JSON)  # Structured feedback for improvement
    last_updated = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class ResumeProcessingSettings(db.Model):
    """Model for storing and managing resume processing settings."""
    id = db.Column(db.Integer, primary_key=True)
    min_match_score = db.Column(db.Float, default=60.0)
    max_candidates = db.Column(db.Integer, default=100)
    analysis_timeout = db.Column(db.Integer, default=300)  # seconds
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('admin.id'))

    def update_from_dict(self, data):
        """Update settings from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """Convert settings object to dictionary."""
        return {
            'id': self.id,
            'min_match_score': self.min_match_score,
            'max_candidates': self.max_candidates,
            'analysis_timeout': self.analysis_timeout,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }


class RankingCriteria(db.Model):
    """Model for storing and managing ranking criteria per job role."""
    id = db.Column(db.Integer, primary_key=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey(
        'job_posting.id'), nullable=False)
    criteria_name = db.Column(db.String(64), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Weight in overall ranking
    min_score = db.Column(db.Float)  # Minimum acceptable score
    max_score = db.Column(db.Float)  # Maximum possible score
    # How this criterion is evaluated
    evaluation_method = db.Column(db.String(32), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)


class JobCategory(db.Model):
    """Model for job categories."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    # Add relationship to job postings
    job_postings = db.relationship('JobPosting', backref='category', lazy=True)
    # Add relationship to AI prompts
    prompts = db.relationship('AIPrompt', backref='job_category', lazy=True)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'job_count': len(self.job_postings) if self.job_postings else 0,
            'prompt_count': len(self.prompts) if self.prompts else 0
        }


class AdminActivity(db.Model):
    """Model for tracking admin activities."""
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    # create, update, delete, login, etc.
    action = db.Column(db.String(32), nullable=False)
    # job_category, ai_prompt, etc.
    resource = db.Column(db.String(32), nullable=True)
    resource_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        """Convert admin activity to dictionary."""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ip_address': self.ip_address
        }
