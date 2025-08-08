from app import create_app, db
from app.models import JobCategory, AIPrompt, Admin
from datetime import datetime, timezone

app = create_app()

with app.app_context():
    # Get all existing job categories
    existing_categories = JobCategory.query.all()
    print(f"Found {len(existing_categories)} existing job categories")

    # Get all job role prompts
    job_role_prompts = AIPrompt.query.filter(AIPrompt.id.between(1, 11)).all()
    print(f"Found {len(job_role_prompts)} job role prompts")

    # Delete existing categories
    for category in existing_categories:
        print(f"Deleting category: {category.id} - {category.name}")
        db.session.delete(category)

    db.session.commit()
    print("Deleted existing categories")

    # Create new categories based on job roles
    new_categories = {}

    for prompt in job_role_prompts:
        if prompt.job_type == "General":
            continue  # Skip the general prompt

        # Create a new category for each job role
        new_category = JobCategory(
            name=prompt.job_type,
            description=f"Job category for {prompt.job_type} positions",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(new_category)
        print(f"Created new category: {prompt.job_type}")

    db.session.commit()
    print("Created new categories")

    # Update the job_category_id for each prompt
    new_categories = {
        category.name: category for category in JobCategory.query.all()}

    for prompt in job_role_prompts:
        if prompt.job_type in new_categories:
            prompt.job_category_id = new_categories[prompt.job_type].id
            print(
                f"Updated prompt {prompt.id} - {prompt.name} with category {new_categories[prompt.job_type].name}")

    db.session.commit()
    print("Updated prompts with new categories")

    # Verify the new categories and prompts
    print("\nNew Job Categories:")
    for category in JobCategory.query.all():
        print(f"ID: {category.id}, Name: {category.name}")

    print("\nUpdated Prompts:")
    for prompt in AIPrompt.query.all():
        category = JobCategory.query.get(
            prompt.job_category_id) if prompt.job_category_id else None
        print(f"ID: {prompt.id}, Name: {prompt.name}, Job Type: {prompt.job_type}, Category: {category.name if category else 'None'}")

    print("\nUpdate complete!")
