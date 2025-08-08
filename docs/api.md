# Resume AI Backend API Documentation

This document provides details about the Resume AI Backend API endpoints, request/response formats, and authentication requirements.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:5000
```

## Authentication

### Admin Authentication

Admin endpoints require JWT authentication using Bearer tokens.

**Login:**

```
POST /admin/login
```

Request body:

```json
{
	"email": "admin@example.com",
	"password": "your-password"
}
```

Response:

```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"expires_at": "2023-03-01T12:00:00Z",
	"admin": {
		"id": 1,
		"username": "admin",
		"email": "admin@example.com"
	}
}
```

**Token Refresh:**

```
POST /admin/refresh-token
```

Request body:

```json
{
	"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:

```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"expires_at": "2023-03-01T13:00:00Z"
}
```

## Resume Endpoints

### Upload Resume

```
POST /api/resume/upload
```

Request:

-    Content-Type: multipart/form-data
-    Fields:
     -    file: Resume file (PDF, DOCX, TXT)
     -    job_role: Job role identifier

Response:

```json
{
	"message": "Resume processed successfully",
	"resume_id": 123,
	"processed_data": {
		"skills": ["Python", "Flask", "SQL"],
		"experience": [
			{
				"title": "Software Engineer",
				"company": "Example Corp",
				"duration": "2 years"
			}
		],
		"education": [
			{
				"degree": "Bachelor of Science",
				"institution": "Example University",
				"year": 2020
			}
		],
		"soft_skills": ["Communication", "Teamwork"]
	},
	"ranking_score": 85.5
}
```

### Get Resume Results

```
GET /api/resume/results/{resume_id}
```

Response:

```json
{
	"processed_data": {
		"skills": ["Python", "Flask", "SQL"],
		"experience": [
			{
				"title": "Software Engineer",
				"company": "Example Corp",
				"duration": "2 years"
			}
		],
		"education": [
			{
				"degree": "Bachelor of Science",
				"institution": "Example University",
				"year": 2020
			}
		],
		"soft_skills": ["Communication", "Teamwork"]
	},
	"ranking_score": 85.5,
	"job_role": "software_engineer"
}
```

## Ranking Endpoints

### Get Rankings for Job

```
GET /api/ranking/job/{job_id}
```

Response:

```json
{
	"job_id": 1,
	"candidates": [
		{
			"resume_id": 123,
			"ranking": 1,
			"score": 85.5,
			"candidate_name": "John Doe",
			"processed_data": {
				"skills": ["Python", "Flask", "SQL"],
				"experience": [
					{
						"title": "Software Engineer",
						"company": "Example Corp",
						"duration": "2 years"
					}
				]
			}
		}
	]
}
```

### Get Alternative Roles

```
GET /api/ranking/alternative-roles/{resume_id}
```

Response:

```json
{
	"resume_id": 123,
	"alternative_roles": [
		{
			"role": "data_scientist",
			"match_score": 75.2,
			"reason": "Strong Python and SQL skills"
		},
		{
			"role": "backend_developer",
			"match_score": 82.1,
			"reason": "Excellent Flask experience"
		}
	]
}
```

### Batch Compare Resumes

```
POST /api/ranking/batch-compare
```

Request body:

```json
{
	"resume_ids": [123, 124, 125],
	"job_id": 1
}
```

Response:

```json
{
	"job_id": 1,
	"job_title": "Software Engineer",
	"comparison_results": [
		{
			"resume_id": 123,
			"candidate_name": "John Doe",
			"ranking_score": 85.5,
			"skills_match": { "Python": 0.9, "Flask": 0.8 },
			"experience_match": 0.75,
			"education_match": 0.9,
			"overall_ranking": 1
		},
		{
			"resume_id": 124,
			"candidate_name": "Jane Smith",
			"ranking_score": 82.3,
			"skills_match": { "Python": 0.8, "Flask": 0.7 },
			"experience_match": 0.8,
			"education_match": 0.85,
			"overall_ranking": 2
		}
	]
}
```

## Admin Endpoints

### Job Management

```
GET /admin/jobs
```

Response:

```json
[
	{
		"id": 1,
		"title": "Software Engineer",
		"department": "Engineering",
		"description": "...",
		"requirements": { "skills": ["Python", "Flask"] },
		"qualifications": { "education": "Bachelor" },
		"skills": { "Python": 0.8, "Flask": 0.7 },
		"experience_level": "Mid-level",
		"status": "active",
		"created_at": "2023-02-25T12:00:00Z"
	}
]
```

```
POST /admin/jobs
```

Request body:

```json
{
	"title": "Data Scientist",
	"department": "Data",
	"description": "...",
	"requirements": { "skills": ["Python", "Machine Learning"] },
	"qualifications": { "education": "Master" },
	"skills": { "Python": 0.9, "Machine Learning": 0.8 },
	"experience_level": "Senior"
}
```

### AI Prompt Management

```
GET /admin/prompts
```

```
POST /admin/prompts
```

```
PUT /admin/prompts
```

### Settings Management

```
GET /admin/settings
```

```
PUT /admin/settings
```

### Analytics

```
GET /admin/analytics
```

Response:

```json
{
  "total_jobs": 10,
  "total_prompts": 5,
  "recent_jobs": [...],
  "recent_prompts": [...],
  "system_status": {
    "ai_service": "operational",
    "database": "connected",
    "last_backup": "2023-02-25T12:00:00Z"
  }
}
```

## Error Responses

All endpoints return standard error responses:

```json
{
	"error": "Error Type",
	"message": "Detailed error message"
}
```

Common HTTP status codes:

-    400: Bad Request
-    401: Unauthorized
-    403: Forbidden
-    404: Not Found
-    429: Too Many Requests
-    500: Internal Server Error
