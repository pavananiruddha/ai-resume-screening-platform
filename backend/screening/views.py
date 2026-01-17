from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import Resume
from .serializers import ResumeSerializer, ScreeningRequestSerializer, ScreeningResultSerializer
from .services import ScreeningService
from .tasks import run_screening_task

class ResumeViewSet(viewsets.ModelViewSet):
    """
    CRUD for Resumes.
    Standard actions: List, Create, Retrieve, Update, Destroy.
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['job', 'status']
    search_fields = ['candidate_name', 'candidate_email']
    ordering_fields = ['score', 'uploaded_at']

    def get_queryset(self):
        # Admin sees all, User sees own.
        # But wait, Resume has 'user' field now.
        user = self.request.user
        if getattr(user, 'role', '') == 'ADMIN':
            return Resume.objects.all().order_by('-uploaded_at')
        return Resume.objects.filter(user=user).order_by('-uploaded_at')

    def perform_create(self, serializer):
        # Set user and trigger extraction
        resume = serializer.save(user=self.request.user)
        try:
            text = ScreeningService.extract_text(resume.resume_file)
            resume.extracted_text = text
            resume.save()
        except Exception as e:
            # Log error but don't fail upload? Or maybe we should?
            print(f"Extraction failed: {e}")

class ScreeningView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Trigger Async Screening",
        description="Enqueues a Celery task to screen the resume against its linked Job description.",
        request=ScreeningRequestSerializer,
        responses={
            202: OpenApiTypes.OBJECT, 
            404: OpenApiTypes.OBJECT
        },
        examples=[
            # Example can be added if needed, usually auto-generated from Serializer is enough
        ]
    )
    def post(self, request):
        serializer = ScreeningRequestSerializer(data=request.data)
        if serializer.is_valid():
            resume_id = serializer.validated_data['resume_id']
            try:
                # Check existance first
                resume = Resume.objects.get(id=resume_id) # Simple check
                
                # Enqueue Task
                task = run_screening_task.delay(resume_id)
                
                return Response({
                    "resume_id": resume_id,
                    "task_id": task.id
                }, status=status.HTTP_202_ACCEPTED)

            except Resume.DoesNotExist:
                return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScreeningStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Check Screening Status",
        description="Poll the status of a screening task.",
        responses={
            200: OpenApiTypes.OBJECT
        }
    )
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": task_result.result,
        }
        return Response(result, status=status.HTTP_200_OK)
