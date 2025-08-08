# Resume AI Backend

A Flask-based backend service for processing and analyzing resumes using AI. The system provides automated resume parsing, skill matching, and candidate ranking capabilities.

## Features

-    Resume parsing and text extraction (PDF, DOCX, TXT)
-    AI-powered resume analysis using OpenAI GPT
-    Candidate ranking and scoring
-    Job posting management
-    Admin panel for system configuration
-    RESTful API endpoints
-    Docker containerization

## Tech Stack

-    Python 3.11
-    Flask 3.0.2
-    PostgreSQL (via SQLAlchemy)
-    OpenAI GPT-4
-    Docker & Docker Compose
-    Redis for caching
-    Celery for background tasks

## Project Structure

```
resume-ai-backend/
├── admin/                 # Admin panel module
├── app/                   # Main application
│   ├── routes/           # API routes
│   ├── models.py         # Database models
│   ├── services.py       # Business logic
│   └── utils.py          # Utility functions
├── config/               # Configuration
├── database/             # Database setup
├── docker/               # Docker configuration
├── static/               # Static assets
├── templates/            # HTML templates
└── tests/                # Test suite
```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/resume-ai-backend.git
cd resume-ai-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:

```bash
flask db upgrade
```

## Running with Docker

1. Build and start the containers:

```bash
docker-compose up --build
```

2. Access the application:

-    API: http://localhost:5000
-    Admin Panel: http://localhost:5000/admin

## API Documentation

### Resume Endpoints

-    `POST /api/resume/upload` - Upload and process a resume
-    `GET /api/resume/results/<id>` - Get processing results

### Ranking Endpoints

-    `GET /api/ranking/job/<id>` - Get rankings for a job
-    `GET /api/ranking/alternative-roles/<id>` - Get role suggestions

### Admin Endpoints

-    `POST /admin/login` - Admin authentication
-    `GET/POST /admin/jobs` - Job posting management
-    `GET/POST /admin/prompts` - AI prompt management

## Testing

Run the test suite:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# resume-scanner
