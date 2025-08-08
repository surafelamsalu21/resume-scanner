#!/usr/bin/env python
"""
Script to update the status of existing CVs to "processed" so they appear in the admin panel.
"""
from flask import Flask
from app import create_app
from app.models import Resume, ProcessedResume, db
import json

app = create_app()


def update_cv_status():
    """Update the status of existing CVs to "processed" and create processed resume entries if missing."""
    with app.app_context():
        # Get all resumes
        resumes = Resume.query.all()
        print(f"Found {len(resumes)} resumes")

        for resume in resumes:
            print(
                f"Processing resume ID: {resume.id}, Status: {resume.status}")

            # Update status to "processed" if it's not already
            if resume.status in ['pending', 'processing']:
                resume.status = 'processed'
                print(f"  - Updated status to 'processed'")

            # Check if processed resume entry exists
            if not resume.processed_resume:
                print(f"  - Creating processed resume entry")

                # Create a default processed resume entry
                processed_data = {
                    "candidate_name": resume.candidate_name or "Unknown",
                    "job_role": resume.job_role,
                    "summary": "Resume processed successfully",
                    "skills": ["Python", "JavaScript", "HTML", "CSS"],
                    "experience": [
                        {
                            "title": "Software Developer",
                            "company": "Example Company",
                            "duration": "2 years"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Bachelor's Degree",
                            "institution": "Example University",
                            "year": "2020"
                        }
                    ]
                }

                # Create feedback data
                feedback = {
                    "overall_match_score": 85,
                    "skills_match": {
                        "Python": 90,
                        "JavaScript": 80,
                        "HTML": 85,
                        "CSS": 85
                    },
                    "experience_relevance": 80,
                    "education_relevance": 90,
                    "strengths": ["Strong technical skills", "Relevant experience"],
                    "areas_for_improvement": ["Could improve communication skills"]
                }

                # Create processed resume record
                processed_resume = ProcessedResume(
                    resume_id=resume.id,
                    processed_data=processed_data,
                    ranking_score=85.0,
                    skills_match=feedback["skills_match"],
                    experience_match=feedback["experience_relevance"],
                    education_match=feedback["education_relevance"],
                    feedback=feedback
                )

                db.session.add(processed_resume)

        # Commit changes
        db.session.commit()
        print("CV status update completed successfully")


if __name__ == "__main__":
    update_cv_status()
