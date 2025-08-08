from app import create_app, db
from app.models import JobCategory, AIPrompt, Admin
from datetime import datetime, timezone

app = create_app()

# Define job roles and their categories
job_role_mapping = {
    "Software Engineer": "Software Development",
    "Data Scientist": "Data Science",
    "Product Manager": "Software Development",
    "UX Designer": "Software Development",
    "Marketing Specialist": "Marketing",
    "Sales Representative": "Marketing",
    "Customer Support": "Marketing",
    "Project Manager": "Software Development",
    "HR Specialist": "Human Resources",
    "Financial Analyst": "Finance"
}

with app.app_context():
    # Get admin user
    admin = Admin.query.first()
    if not admin:
        print("No admin user found. Please run seed_data.py first.")
        exit(1)

    # Get all job categories
    categories = {
        category.name: category for category in JobCategory.query.all()}
    print(f"Found {len(categories)} job categories")

    # Check if all required categories exist
    required_categories = set(job_role_mapping.values())
    missing_categories = required_categories - set(categories.keys())

    if missing_categories:
        print(f"Missing categories: {missing_categories}")
        print("Please run seed_data.py to create all required categories.")
        exit(1)

    # For each job role, ensure there's a corresponding prompt
    prompts_created = 0
    for job_role, category_name in job_role_mapping.items():
        # Get the category
        category = categories[category_name]

        # Check if a prompt already exists for this job role
        existing_prompt = AIPrompt.query.filter_by(
            job_type=job_role
        ).first()

        if existing_prompt:
            print(
                f"Prompt for {job_role} already exists (ID: {existing_prompt.id})")
            continue

        # Create a new prompt for this job role
        prompt_template = f"""
Analyze the following resume against the job description for a {job_role} role:

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
    "summary": "Brief summary of the candidate's fit for the {job_role} role"
}}

Focus on evaluating the candidate's skills, experience, and qualifications relevant to {job_role} positions. Provide specific recommendations for how the candidate can improve their resume for this role.
"""

        prompt = AIPrompt(
            name=f"{job_role} Resume Analysis",
            description=f"Analyzes resumes for {job_role.lower()} positions",
            prompt_template=prompt_template,
            job_type=job_role,
            version="1.0",
            is_active=True,
            job_category_id=category.id,
            admin_id=admin.id
        )

        db.session.add(prompt)
        prompts_created += 1

    # Commit changes
    db.session.commit()
    print(f"Created {prompts_created} new AI prompts")

    # Print current prompts for job roles
    print("\nCurrent Job Role Prompts:")
    for job_role in job_role_mapping.keys():
        prompt = AIPrompt.query.filter_by(job_type=job_role).first()
        if prompt:
            category = JobCategory.query.get(
                prompt.job_category_id) if prompt.job_category_id else None
            print(
                f"Job Role: {job_role}, Prompt ID: {prompt.id}, Category: {category.name if category else 'None'}")
        else:
            print(f"No prompt found for job role: {job_role}")
