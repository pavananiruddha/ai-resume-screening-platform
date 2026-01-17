import re
import os
from pypdf import PdfReader
from django.conf import settings
from .models import Resume

class ScreeningService:
    @staticmethod
    def extract_text(resume_file):
        """
        Extracts text from a resume file (PDF or text).
        """
        try:
            file_path = resume_file.path
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            if ext == '.pdf':
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            elif ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                # Fallback for other formats or return empty
                # For now, just return empty string or raise error
                return ""
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    @staticmethod
    def calculate_score(resume_text, job_description):
        """
        Calculates a score based on keyword matching between resume text and job description.
        Simple implementation:
        1. Tokenize job description to find potential keywords (ignoring short words).
        2. Count how many of these keywords appear in the resume.
        3. Score = (Matches / Total Keywords) * 100.
        """
        if not resume_text or not job_description:
            return 0.0, []

        # Simple tokenization: remove non-alphanumeric, lowercase, split
        def tokenize(text):
            return set(re.findall(r'\b\w{4,}\b', text.lower()))

        job_keywords = tokenize(job_description)
        resume_tokens = tokenize(resume_text)
        
        if not job_keywords:
            return 0.0, []

        matches = job_keywords.intersection(resume_tokens)
        score = (len(matches) / len(job_keywords)) * 100
        
        return round(score, 2), list(matches)

    @classmethod
    def screen_resume(cls, resume_id):
        try:
            resume = Resume.objects.get(id=resume_id)
            job = resume.job
            
            # Update status
            resume.status = 'PROCESSING'
            resume.save()

            # Use extracted text if available, else extract
            resume_text = resume.extracted_text
            if not resume_text:
                resume_text = cls.extract_text(resume.resume_file)
                resume.extracted_text = resume_text
                resume.save()
            
            # Calculate score
            score, matched_keywords = cls.calculate_score(resume_text, job.description)
            
            # Update resume
            resume.score = score
            resume.status = 'SHORTLISTED' if score > 50 else 'REJECTED' # Simple threshold
            resume.save()
            
            return {
                "id": resume.id,
                "score": score,
                "status": resume.status,
                "matched_keywords": matched_keywords
            }

        except Resume.DoesNotExist:
            raise ValueError("Resume found not found")
        except Exception as e:
            if 'resume' in locals():
                resume.status = 'PENDING' # Revert or error state
                resume.save()
            raise e
