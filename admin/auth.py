from flask import request, jsonify, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from datetime import datetime
from app.models import Admin, AdminActivity, db
import logging
from admin import admin_bp

# Configure logging
logger = logging.getLogger(__name__)

# Create a simple login form with CSRF protection


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login endpoint."""
    logger.info("Login route accessed")

    # Create a form instance
    form = LoginForm()

    # For GET requests, render the login form
    if request.method == 'GET':
        return render_template('admin_login.html', form=form)

    # For POST requests, validate the form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        logger.info(f"Login attempt for email: {email}")

        admin = Admin.query.filter_by(email=email).first()

        if not admin or not admin.check_password(password):
            logger.error("Invalid email or password")
            return render_template('admin_login.html', form=form, error='Invalid email or password')

        # Generate tokens
        access_token = admin.generate_access_token()
        refresh_token = admin.generate_refresh_token()

        # Update last login timestamp
        admin.last_login = datetime.utcnow()
        db.session.commit()

        # Log activity
        activity = AdminActivity(
            admin_id=admin.id,
            action='login',
            resource='admin',
            resource_id=admin.id,
            details=f"Admin login: {admin.email}"
        )
        db.session.add(activity)
        db.session.commit()

        # Redirect to dashboard
        response = redirect(url_for('admin.dashboard'))

        # Set secure cookies
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            max_age=86400,  # 1 day
            secure=request.is_secure,
            samesite='Lax'
        )
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            max_age=2592000,  # 30 days
            secure=request.is_secure,
            samesite='Lax'
        )

        logger.info(f"Login successful for {email}, redirecting to dashboard")
        return response

    # If form validation fails
    logger.error(f"Form validation failed: {form.errors}")
    return render_template('admin_login.html', form=form, error='Invalid form submission')
