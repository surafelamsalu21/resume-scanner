from app import create_app, db
from app.models import JobCategory, AIPrompt, Admin
from datetime import datetime, timezone

app = create_app()

with app.app_context():
    # Get all AI prompts
    all_prompts = AIPrompt.query.all()
    print(f"Found {len(all_prompts)} AI prompts")

    # Identify category-level prompts (IDs 12-16)
    category_prompts = AIPrompt.query.filter(AIPrompt.id.between(12, 16)).all()
    print(f"Found {len(category_prompts)} category-level prompts")

    # Delete category-level prompts
    for prompt in category_prompts:
        print(f"Deleting prompt: {prompt.id} - {prompt.name}")
        db.session.delete(prompt)

    # Commit changes
    db.session.commit()
    print("Deleted category-level prompts")

    # Verify specific job role prompts
    job_role_prompts = AIPrompt.query.filter(AIPrompt.id.between(1, 11)).all()
    print(f"\nRemaining job role prompts ({len(job_role_prompts)}):")
    for prompt in job_role_prompts:
        category = JobCategory.query.get(
            prompt.job_category_id) if prompt.job_category_id else None
        print(f"ID: {prompt.id}, Name: {prompt.name}, Job Type: {prompt.job_type}, Category: {category.name if category else 'None'}")

    print("\nCleanup complete!")
