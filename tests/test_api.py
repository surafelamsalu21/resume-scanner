import pytest
import json
import os
from app import create_app
from database.db import db
from app.models import Admin, JobPosting, Resume, ProcessedResume
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Set the testing configuration
    os.environ['FLASK_ENV'] = 'testing'

    # Create the Flask app
    app = create_app('testing')

    # Create the database and tables
    with app.app_context():
        db.create_all()

        # Create test admin user
        admin = Admin(
            username='testadmin',
            email='admin@test.com',
            is_active=True
        )
        admin.password_hash = generate_password_hash('testpassword')
        db.session.add(admin)

        # Create test job posting
        job = JobPosting(
            title='Test Job',
            department='Engineering',
            description='Test job description',
            requirements={'skills': ['Python', 'Flask']},
            qualifications={'education': 'Bachelor'},
            skills={'Python': 0.8, 'Flask': 0.7},
            experience_level='Mid-level',
            created_at=datetime.utcnow(),
            admin_id=1
        )
        db.session.add(job)

        db.session.commit()

    yield app

    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def admin_token(client):
    """Get a valid admin token."""
    response = client.post(
        '/admin/login',
        json={'email': 'admin@test.com', 'password': 'testpassword'}
    )
    data = json.loads(response.data)
    return data['access_token']


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_admin_login(client):
    """Test admin login."""
    # Test with valid credentials
    response = client.post(
        '/admin/login',
        json={'email': 'admin@test.com', 'password': 'testpassword'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data

    # Test with invalid credentials
    response = client.post(
        '/admin/login',
        json={'email': 'admin@test.com', 'password': 'wrongpassword'}
    )
    assert response.status_code == 401


def test_token_refresh(client, admin_token):
    """Test token refresh."""
    # First get a refresh token
    response = client.post(
        '/admin/login',
        json={'email': 'admin@test.com', 'password': 'testpassword'}
    )
    data = json.loads(response.data)
    refresh_token = data['refresh_token']

    # Test token refresh
    response = client.post(
        '/admin/refresh-token',
        json={'refresh_token': refresh_token}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'expires_at' in data


def test_get_jobs(client, admin_token):
    """Test getting job postings."""
    response = client.get(
        '/admin/jobs',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['title'] == 'Test Job'


def test_unauthorized_access(client):
    """Test unauthorized access to protected routes."""
    response = client.get('/admin/jobs')
    assert response.status_code == 401

    response = client.get(
        '/admin/jobs',
        headers={'Authorization': 'Bearer invalid_token'}
    )
    assert response.status_code == 401
