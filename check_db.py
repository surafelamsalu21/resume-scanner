from app import create_app
from app.models import JobCategory, AIPrompt

app = create_app()

with app.app_context():
    job_categories = JobCategory.query.all()
    ai_prompts = AIPrompt.query.all()

    print("Job Categories:")
    if job_categories:
        for category in job_categories:
            print(f"ID: {category.id}, Name: {category.name}")
    else:
        print("No job categories found in the database.")

    print("\nAI Prompts:")
    if ai_prompts:
        for prompt in ai_prompts:
            print(
                f"ID: {prompt.id}, Name: {prompt.name}, Job Type: {prompt.job_type}")
    else:
        print("No AI prompts found in the database.")
