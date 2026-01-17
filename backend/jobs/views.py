from rest_framework import viewsets, permissions, filters
from .models import Job
from .serializers import JobSerializer

class IsAdminOrHR(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', '') in ['ADMIN', 'HR']

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
