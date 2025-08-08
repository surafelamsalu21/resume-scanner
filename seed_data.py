from app import create_app, db
from app.models import JobCategory, AIPrompt, Admin
from datetime import datetime, timezone
import bcrypt

app = create_app()

# Resume analysis prompt template
resume_analysis_prompt = """
Analyze the following resume and extract key information:

RESUME:
{resume_text}

Please provide a detailed analysis in JSON format with the following structure:
{
    "candidate_name": "Full name of the candidate",
    "contact_info": {
        "email": "Email address",
        "phone": "Phone number",
        "location": "Location"
    },
    "skills": [
        {"name": "Skill name", "level": "Advanced"}
    ],
    "experience": [
        {
            "title": "Job title",
            "company": "Company name",
            "duration": "Duration in years",
            "description": "Brief description"
        }
    ],
    "education": [
        {
            "degree": "Degree name",
            "institution": "Institution name",
            "field": "Field of study",
            "year": "Year completed"
        }
    ],
    "summary": "Brief professional summary"
}

Ensure all fields are filled based on the resume content. If information is not available, use null or empty arrays.
"""

# Job description match prompt template
job_match_prompt = """
Analyze how well the following resume matches the job description:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 85,
    "skills_match": [
        {"skill": "Python", "match_percentage": 90, "level": "Advanced"},
        {"skill": "Machine Learning", "match_percentage": 85, "level": "Advanced"}
    ],
    "experience_relevance": 80,
    "education_relevance": 90,
    "strengths": ["Strong technical skills", "Relevant experience"],
    "weaknesses": ["Missing specific technology X"],
    "recommendations": ["Highlight project Y more prominently"],
    "summary": "Strong candidate with relevant skills and experience"
}

Be honest and accurate in your assessment. The overall_match_score should be a number between 0 and 100.
"""

with app.app_context():
    # Check if there's an admin user
    admin = Admin.query.first()
    if not admin:
        # Create an admin user if none exists
        hashed_password = bcrypt.hashpw('admin123'.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = Admin(
            username='admin',
            email='admin@example.com',
            password=hashed_password,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")

    # Create job categories if none exist
    if JobCategory.query.count() == 0:
        categories = [
            JobCategory(
                name="Software Development",
                description="Roles related to software engineering, development, and programming",
                is_active=True
            ),
            JobCategory(
                name="Data Science",
                description="Roles related to data analysis, machine learning, and AI",
                is_active=True
            ),
            JobCategory(
                name="Marketing",
                description="Roles related to digital marketing, content creation, and brand management",
                is_active=True
            ),
            JobCategory(
                name="Finance",
                description="Roles related to accounting, financial analysis, and banking",
                is_active=True
            ),
            JobCategory(
                name="Human Resources",
                description="Roles related to HR management, recruitment, and employee relations",
                is_active=True
            )
        ]

        db.session.add_all(categories)
        db.session.commit()
        print(f"Created {len(categories)} job categories")

    # Create AI prompts if none exist
    if AIPrompt.query.count() == 0:
        # Get the categories
        software_category = JobCategory.query.filter_by(
            name="Software Development").first()
        data_category = JobCategory.query.filter_by(
            name="Data Science").first()
        marketing_category = JobCategory.query.filter_by(
            name="Marketing").first()

        prompts = [
            AIPrompt(
                name="Software Engineer Resume Analysis",
                description="Analyzes software engineering resumes against job descriptions",
                prompt_template=job_match_prompt,
                job_type="Software Engineer",
                version="1.0",
                is_active=True,
                job_category_id=software_category.id if software_category else None,
                admin_id=admin.id
            ),
            AIPrompt(
                name="Data Scientist Resume Analysis",
                description="Analyzes data science resumes against job descriptions",
                prompt_template=job_match_prompt,
                job_type="Data Scientist",
                version="1.0",
                is_active=True,
                job_category_id=data_category.id if data_category else None,
                admin_id=admin.id
            ),
            AIPrompt(
                name="Marketing Specialist Resume Analysis",
                description="Analyzes marketing resumes against job descriptions",
                prompt_template=job_match_prompt,
                job_type="Marketing Specialist",
                version="1.0",
                is_active=True,
                job_category_id=marketing_category.id if marketing_category else None,
                admin_id=admin.id
            ),
            AIPrompt(
                name="Resume Information Extraction",
                description="Extracts structured information from resumes",
                prompt_template=resume_analysis_prompt,
                job_type="General",
                version="1.0",
                is_active=True,
                job_category_id=None,  # General prompt, not tied to a specific category
                admin_id=admin.id
            )
        ]

        db.session.add_all(prompts)
        db.session.commit()
        print(f"Created {len(prompts)} AI prompts")

    print("\nCurrent Database State:")
    print("Job Categories:")
    for category in JobCategory.query.all():
        print(f"ID: {category.id}, Name: {category.name}")

    print("\nAI Prompts:")
    for prompt in AIPrompt.query.all():
        print(
            f"ID: {prompt.id}, Name: {prompt.name}, Job Type: {prompt.job_type}")
