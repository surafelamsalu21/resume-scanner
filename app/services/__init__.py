"""
Services module for resume processing and AI analysis.
"""
import os
import logging
from typing import Dict, Tuple, Any, Optional, List
import json
from flask import current_app
from app.utils import AIProcessor, preprocess_resume
from app.models import AIPrompt, JobPosting, JobCategory

logger = logging.getLogger(__name__)


class ResumeProcessor:
    """Service for processing resume files."""

    def extract_text_from_file(self, file_path: str, mime_type: str) -> str:
        """Extract text content from uploaded file."""
        try:
            current_app.logger.info(
                f"Extracting text from file: {file_path} (MIME: {mime_type})")

            if mime_type == 'application/pdf':
                return self._extract_from_pdf(file_path)
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return self._extract_from_docx(file_path)
            elif mime_type == 'text/plain':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported MIME type: {mime_type}")

        except Exception as e:
            current_app.logger.error(
                f"Error extracting text from file: {str(e)}")
            # Return a clear error message that will be useful for debugging
            return f"ERROR EXTRACTING TEXT: {str(e)}"

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2

            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"

            # If PyPDF2 returns empty text, try with pdfplumber as backup
            if not text.strip():
                current_app.logger.info(
                    "PyPDF2 extracted empty text, trying pdfplumber")
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or "" + "\n"

            current_app.logger.info(
                f"Extracted {len(text)} characters from PDF")
            return text

        except Exception as e:
            current_app.logger.error(
                f"Error extracting text from PDF: {str(e)}")
            raise

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            import docx

            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

            current_app.logger.info(
                f"Extracted {len(text)} characters from DOCX")
            return text

        except Exception as e:
            current_app.logger.error(
                f"Error extracting text from DOCX: {str(e)}")
            raise

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            current_app.logger.info(
                f"Extracted {len(text)} characters from TXT")
            return text

        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()

            current_app.logger.info(
                f"Extracted {len(text)} characters from TXT (latin-1 encoding)")
            return text
        except Exception as e:
            current_app.logger.error(
                f"Error extracting text from TXT: {str(e)}")
            raise


class AIService:
    """Service for AI-powered resume processing."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processor = AIProcessor()

    def process_resume(self, text_content: str, job_role: str) -> Tuple[Dict[str, Any], float]:
        """Process a resume for a generic job role."""
        try:
            self.logger.info(f"Processing resume for job role: {job_role}")

            # Check if text extraction had an error
            if text_content.startswith("ERROR EXTRACTING TEXT:"):
                error_msg = text_content
                self.logger.error(f"Text extraction error: {error_msg}")
                return {
                    "error": error_msg,
                    "job_role": job_role,
                    "candidate_name": "Error",
                    "summary": "Error extracting text from resume"
                }, 0

            # Check if we have enough text to process
            if len(text_content.strip()) < 100:
                self.logger.error(
                    f"Insufficient text content: {len(text_content)} characters")
                return {
                    "error": "Insufficient text content in resume",
                    "job_role": job_role,
                    "candidate_name": "Error",
                    "summary": "The resume doesn't contain enough text to analyze"
                }, 0

            # Log the first 500 characters of text for debugging
            self.logger.info(f"Resume text preview: {text_content[:500]}...")

            # Process with OpenAI
            try:
                # Get AI analysis of the resume
                analysis = self.processor.analyze_resume(text_content)

                # Get a generic job description for this role
                job_prompt = AIPrompt.query.filter_by(
                    job_type=job_role,
                    is_active=True
                ).order_by(AIPrompt.updated_at.desc()).first()

                job_description = ""
                if job_prompt:
                    # Extract just the job description part from the prompt template
                    # The prompt template might contain placeholders like {resume_text} and {job_description}
                    # We need to create a proper job description without these placeholders
                    self.logger.info(
                        f"Using job prompt template for {job_role}")

                    # Create a detailed job description based on the role
                    job_description = f"""
                    Job Title: {job_role}
                    
                    Description:
                    We are looking for an experienced {job_role} to join our team. The ideal candidate will have a strong background in relevant technologies and methodologies.
                    
                    Required Skills:
                    - Technical expertise relevant to {job_role}
                    - Problem-solving abilities
                    - Communication skills
                    - Teamwork and collaboration
                    - Attention to detail
                    
                    Qualifications:
                    - Bachelor's degree in a relevant field
                    - 3+ years of experience in similar roles
                    - Proven track record of successful projects
                    
                    This job description is based on the {job_role} prompt template in our system.
                    """
                else:
                    # Fallback generic job description
                    self.logger.warning(
                        f"No job prompt found for {job_role}, using fallback description")
                    job_description = f"""
                    Job Title: {job_role}
                    
                    Description:
                    We are looking for a skilled {job_role} with relevant experience and expertise.
                    
                    Required Skills:
                    - Strong technical skills relevant to the role
                    - Experience in similar positions
                    - Good communication and teamwork abilities
                    - Problem-solving skills
                    - Adaptability and willingness to learn
                    
                    Qualifications:
                    - Relevant education or certification
                    - Experience in the field
                    - Professional attitude and work ethic
                    
                    This is a generic job description for {job_role} position.
                    """

                self.logger.info(
                    f"Job description length: {len(job_description)} characters")
                self.logger.debug(
                    f"Job description preview: {job_description[:200]}...")

                # Get match analysis
                match_analysis = self.processor.generate_job_description_match(
                    text_content,
                    job_description
                )

                # Combine all data
                processed_data = {
                    **analysis,
                    **match_analysis,
                    'job_role': job_role
                }

                # Get the overall match score
                ranking_score = match_analysis.get('overall_match_score', 0)

                return processed_data, ranking_score

            except Exception as e:
                self.logger.error(f"OpenAI processing error: {str(e)}")
                import traceback
                self.logger.error(traceback.format_exc())

                # Fallback to basic processing if OpenAI fails
                return {
                    "error": f"AI processing error: {str(e)}",
                    "job_role": job_role,
                    "candidate_name": "Error",
                    "summary": "Error during AI processing of resume",
                    "raw_text": text_content[:1000] + "..." if len(text_content) > 1000 else text_content
                }, 0

        except Exception as e:
            self.logger.error(f"Error processing resume: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "job_role": job_role,
                "candidate_name": "Error",
                "summary": "Error processing resume"
            }, 0

    def process_resume_with_job(self, text_content: str, job_role: str, job_id: int) -> Tuple[Dict[str, Any], float]:
        """Process a resume for a specific job posting."""
        try:
            self.logger.info(f"Processing resume for job ID: {job_id}")

            # Get the job posting
            job_posting = JobPosting.query.get(job_id)
            if not job_posting:
                self.logger.error(f"Job posting not found: {job_id}")
                return self.process_resume(text_content, job_role)

            # Preprocess the resume text
            preprocessed_data = preprocess_resume(text_content)

            # Get AI analysis of the resume
            analysis = self.processor.analyze_resume(
                preprocessed_data['cleaned_text'])

            # Create job description from job posting
            job_description = f"Job Title: {job_posting.title}\n"
            job_description += f"Department: {job_posting.department}\n"
            job_description += f"Description: {job_posting.description}\n"
            job_description += "Required Skills:\n"
            for skill, weight in job_posting.skills.items():
                job_description += f"- {skill} (Importance: {weight*100:.0f}%)\n"
            job_description += "Qualifications:\n"
            for qual_type, qual in job_posting.qualifications.items():
                job_description += f"- {qual_type}: {qual}\n"

            # Get match analysis
            match_analysis = self.processor.generate_job_description_match(
                preprocessed_data['cleaned_text'],
                job_description
            )

            # Get job category information
            job_category = None
            if job_posting.category_id:
                job_category = JobCategory.query.get(job_posting.category_id)

            # Combine all data
            processed_data = {
                **analysis,
                **match_analysis,
                'job_role': job_role,
                'job_title': job_posting.title,
                'job_department': job_posting.department,
                'job_id': job_posting.id,
                'job_category': job_category.name if job_category else None,
                'job_category_id': job_category.id if job_category else None
            }

            # Get the overall match score
            ranking_score = match_analysis.get('overall_match_score', 0)

            return processed_data, ranking_score

        except Exception as e:
            self.logger.error(f"Error processing resume with job: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "job_role": job_role,
                "job_id": job_id,
                "candidate_name": "Error",
                "summary": "Error processing resume"
            }, 0


class RankingService:
    """
    Handles ranking and comparison of resumes against job postings.
    """

    def rank_resumes(self, job_posting_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Rank resumes for a specific job posting.

        Args:
            job_posting_id: ID of the job posting
            limit: Maximum number of results to return

        Returns:
            List of ranked resume data
        """
        logger.info(f"Ranking resumes for job posting ID: {job_posting_id}")

        # In a real implementation, this would query the database and apply ranking algorithms
        # For now, we'll just return mock data

        ranked_resumes = [
            {
                "resume_id": 1,
                "candidate_name": "Candidate A",
                "ranking_score": 92.5,
                "skills_match": 0.9,
                "experience_match": 0.85,
                "education_match": 0.95,
                "overall_ranking": 1
            },
            {
                "resume_id": 2,
                "candidate_name": "Candidate B",
                "ranking_score": 87.3,
                "skills_match": 0.85,
                "experience_match": 0.9,
                "education_match": 0.8,
                "overall_ranking": 2
            },
            {
                "resume_id": 3,
                "candidate_name": "Candidate C",
                "ranking_score": 78.6,
                "skills_match": 0.75,
                "experience_match": 0.8,
                "education_match": 0.85,
                "overall_ranking": 3
            }
        ]

        return ranked_resumes[:limit]

    def compare_resumes(self, resume_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple resumes side by side.

        Args:
            resume_ids: List of resume IDs to compare

        Returns:
            Comparison data
        """
        logger.info(f"Comparing resumes: {resume_ids}")

        # In a real implementation, this would fetch and compare actual resume data
        # For now, we'll just return mock data

        comparison = {
            "resumes": [
                {
                    "resume_id": 1,
                    "candidate_name": "Candidate A",
                    "ranking_score": 92.5,
                    "top_skills": ["Python", "Flask", "SQL"],
                    "years_experience": 5
                },
                {
                    "resume_id": 2,
                    "candidate_name": "Candidate B",
                    "ranking_score": 87.3,
                    "top_skills": ["JavaScript", "React", "Node.js"],
                    "years_experience": 3
                }
            ],
            "comparison_metrics": {
                "skills_overlap": ["Python", "JavaScript"],
                "experience_difference": 2,
                "education_similarity": 0.7
            }
        }

        return comparison
