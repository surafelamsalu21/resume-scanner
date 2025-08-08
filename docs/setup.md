# Setup Guide for Resume AI Backend

This guide provides instructions for setting up and running the Resume AI Backend application both locally and using Docker.

## Local Setup

### Prerequisites

-    Python 3.11 or higher
-    PostgreSQL database
-    Redis (optional, for caching and rate limiting)

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/resume-ai-backend.git
cd resume-ai-backend
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application**

```bash
python run.py
```

The application will be available at http://localhost:5000

### Running Tests

To run the tests locally:

```bash
pytest
```

For more detailed test output:

```bash
pytest -v
```

## Docker Setup

### Prerequisites

-    Docker
-    Docker Compose

### Running with Docker Compose

1. **Build and start the containers**

```bash
cd docker
docker-compose up -d
```

This will start:

-    The Flask application
-    PostgreSQL database
-    Redis (if configured)

2. **Check container status**

```bash
docker-compose ps
```

3. **View logs**

```bash
docker-compose logs -f
```

The application will be available at http://localhost:5000

### Running Tests in Docker

To run tests in the Docker environment:

```bash
docker-compose exec backend pytest
```

## API Documentation

Once the application is running, you can access the API documentation at:

-    Local: http://localhost:5000/docs/api.md

## Troubleshooting

### Common Issues

1. **Database connection errors**

     - Check your database credentials in the `.env` file
     - Ensure PostgreSQL is running

2. **Port conflicts**

     - If port 5000 is already in use, modify the `PORT` variable in your `.env` file

3. **Docker issues**
     - Ensure Docker daemon is running
     - Try rebuilding with `docker-compose build --no-cache`

### Getting Help

If you encounter any issues, please:

1. Check the logs for error messages
2. Refer to the project documentation
3. Open an issue on the GitHub repository
