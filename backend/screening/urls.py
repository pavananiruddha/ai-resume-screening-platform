from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScreeningView, ScreeningStatusView, ResumeViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resumes')

urlpatterns = [
    path('run/', ScreeningView.as_view(), name='screening-run'),
    path('status/<str:task_id>/', ScreeningStatusView.as_view(), name='screening-status'),
    path('', include(router.urls)),
]
