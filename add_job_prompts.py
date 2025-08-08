from app import create_app, db
from app.models import JobCategory, AIPrompt, Admin
from datetime import datetime, timezone

app = create_app()

# Specialized prompt templates for different job roles
prompt_templates = {
    "Product Manager": """
Analyze the following resume against the job description for a Product Manager role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "Product Strategy", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Market Research", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Stakeholder Management", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Product Development", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Agile Methodologies", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the Product Manager role"
}

Focus on evaluating the candidate's experience with product lifecycle management, stakeholder communication, market analysis, and product strategy development. Assess their ability to translate business requirements into product features and their track record of successful product launches.
""",

    "UX Designer": """
Analyze the following resume against the job description for a UX Designer role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "UI/UX Design", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "User Research", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Wireframing", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Prototyping", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Design Tools", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the UX Designer role"
}

Focus on evaluating the candidate's design portfolio, user-centered design approach, proficiency with design tools (Figma, Sketch, Adobe XD), and understanding of usability principles. Assess their ability to create intuitive user interfaces and conduct effective user research.
""",

    "Sales Representative": """
Analyze the following resume against the job description for a Sales Representative role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "Sales Techniques", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Negotiation", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "CRM Software", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Lead Generation", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Client Relationship", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the Sales Representative role"
}

Focus on evaluating the candidate's sales performance metrics, negotiation skills, experience with CRM systems, and ability to build and maintain client relationships. Assess their track record in meeting or exceeding sales targets and their approach to prospecting and closing deals.
""",

    "Customer Support": """
Analyze the following resume against the job description for a Customer Support role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "Communication", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Problem Solving", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Technical Support", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Customer Service", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Ticketing Systems", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the Customer Support role"
}

Focus on evaluating the candidate's communication skills, problem-solving abilities, patience, and experience with customer service tools and ticketing systems. Assess their ability to handle difficult customer situations and their track record of resolving customer issues efficiently.
""",

    "Project Manager": """
Analyze the following resume against the job description for a Project Manager role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "Project Planning", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Team Leadership", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Budget Management", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Risk Management", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Project Tools", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the Project Manager role"
}

Focus on evaluating the candidate's experience with project management methodologies (Agile, Scrum, Waterfall), ability to lead cross-functional teams, track record of delivering projects on time and within budget, and proficiency with project management tools. Assess their communication skills and ability to manage stakeholder expectations.
""",

    "HR Specialist": """
Analyze the following resume against the job description for an HR Specialist role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "Recruitment", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Employee Relations", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "HR Policies", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Benefits Administration", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "HR Compliance", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the HR Specialist role"
}

Focus on evaluating the candidate's knowledge of HR practices, experience with HRIS systems, understanding of employment laws and regulations, and ability to handle sensitive employee matters. Assess their communication skills and experience with full-cycle recruitment, onboarding, and employee development.
""",

    "Financial Analyst": """
Analyze the following resume against the job description for a Financial Analyst role:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please provide a detailed analysis in JSON format with the following structure:
{
    "overall_match_score": 0-100,
    "skills_match": [
        {"skill": "Financial Modeling", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Data Analysis", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Accounting", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Financial Reporting", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"},
        {"skill": "Excel/Financial Software", "match_percentage": 0-100, "level": "Beginner/Intermediate/Advanced"}
    ],
    "experience_relevance": 0-100,
    "education_relevance": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "summary": "Brief summary of the candidate's fit for the Financial Analyst role"
}

Focus on evaluating the candidate's financial analysis skills, proficiency with financial software and Excel, understanding of accounting principles, and experience with budgeting and forecasting. Assess their ability to interpret financial data and communicate financial insights to non-financial stakeholders.
"""
}

with app.app_context():
    # Get admin user
    admin = Admin.query.first()
    if not admin:
        print("No admin user found. Please run seed_data.py first.")
        exit(1)

    # Get job categories
    software_category = JobCategory.query.filter_by(
        name="Software Development").first()
    data_category = JobCategory.query.filter_by(name="Data Science").first()
    marketing_category = JobCategory.query.filter_by(name="Marketing").first()
    finance_category = JobCategory.query.filter_by(name="Finance").first()
    hr_category = JobCategory.query.filter_by(name="Human Resources").first()

    # Map job roles to categories
    category_mapping = {
        "Product Manager": software_category,
        "UX Designer": software_category,
        "Sales Representative": marketing_category,
        "Customer Support": marketing_category,
        "Project Manager": software_category,
        "HR Specialist": hr_category,
        "Financial Analyst": finance_category
    }

    # Create prompts for each job role
    prompts_created = 0
    for job_role, prompt_template in prompt_templates.items():
        # Check if prompt already exists
        existing_prompt = AIPrompt.query.filter_by(
            name=f"{job_role} Resume Analysis").first()
        if existing_prompt:
            print(f"Prompt for {job_role} already exists. Skipping.")
            continue

        category = category_mapping.get(job_role)
        if not category:
            print(f"No category found for {job_role}. Skipping.")
            continue

        # Create new prompt
        prompt = AIPrompt(
            name=f"{job_role} Resume Analysis",
            description=f"Analyzes {job_role.lower()} resumes against job descriptions",
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

    # Print current prompts
    print("\nCurrent AI Prompts:")
    for prompt in AIPrompt.query.all():
        category = JobCategory.query.get(
            prompt.job_category_id) if prompt.job_category_id else None
        print(f"ID: {prompt.id}, Name: {prompt.name}, Job Type: {prompt.job_type}, Category: {category.name if category else 'None'}")
