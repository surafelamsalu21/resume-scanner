from app import create_app, db
from app.models import JobCategory, AIPrompt, Admin
from datetime import datetime, timezone

app = create_app()

# Template for job category prompts


def create_prompt_template(category_name):
    return f"""
Analyze the following resume against the job description for a {category_name} role:

RESUME:
{{resume_text}}

JOB DESCRIPTION:
{{job_description}}

Please provide a detailed analysis in JSON format with the following structure:
{{
    "overall_match_score": 0-100,
    "skills_match": [
        {{"skill": "Skill name", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the {category_name} role"
}}

Focus on evaluating the candidate's skills, experience, and qualifications relevant to {category_name} positions. Provide specific recommendations for how the candidate can improve their resume for this role.
"""


with app.app_context():
    # Get admin user
    admin = Admin.query.first()
    if not admin:
        print("No admin user found. Please run seed_data.py first.")
        exit(1)

    # Get all job categories
    categories = JobCategory.query.all()
    print(f"Found {len(categories)} job categories")

    # For each category, ensure there's a corresponding prompt
    prompts_created = 0
    for category in categories:
        # Check if a prompt already exists for this category
        existing_prompt = AIPrompt.query.filter_by(
            job_type=category.name,
            job_category_id=category.id
        ).first()

        if existing_prompt:
            print(
                f"Prompt for {category.name} already exists (ID: {existing_prompt.id})")
            continue

        # Create a new prompt for this category
        prompt = AIPrompt(
            name=f"{category.name} Resume Analysis",
            description=f"Analyzes resumes for {category.name.lower()} positions",
            prompt_template=create_prompt_template(category.name),
            job_type=category.name,
            version="1.0",
            is_active=category.is_active,
            job_category_id=category.id,
            admin_id=admin.id
        )

        db.session.add(prompt)
        prompts_created += 1

    # Commit changes
    db.session.commit()
    print(f"Created {prompts_created} new AI prompts")

    # Print current prompts
    print("\nCurrent AI Prompts:")
    for prompt in AIPrompt.query.all():
        category = JobCategory.query.get(
            prompt.job_category_id) if prompt.job_category_id else None
        print(f"ID: {prompt.id}, Name: {prompt.name}, Job Type: {prompt.job_type}, Category: {category.name if category else 'None'}")
