from celery import shared_task
from .services import ScreeningService

@shared_task
def run_screening_task(resume_id):
    """
    Async wrapper for screening service.
    """
    try:
        result = ScreeningService.screen_resume(resume_id)
        return result
    except Exception as e:
        # Log failure to DB
        from .models import Resume
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.status = 'REJECTED' # Or 'FAILED' if we add that status
            resume.error_details = str(e)
            resume.save()
        except Resume.DoesNotExist:
            pass
        return {"error": str(e)}
