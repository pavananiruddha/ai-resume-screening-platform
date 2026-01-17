from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # AllowAny so we can reach it, but perform_create handles restriction
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data
        requested_role = validated_data.get('role', 'HR') # Default to HR if not specified? 
        
        # Requirement: "Add permissions so only ADMIN can create HR users."
        # Use Case 1: First Run. No users. We need to Create Superuser via CLI.
        # Use Case 2: Admin logs in. Creates HR user.
        # Use Case 3: Random person hits endpoint. Tries to create HR. Should fail.
        
        if requested_role in ['HR', 'ADMIN']:
             if not (user.is_authenticated and getattr(user, 'role', '') == 'ADMIN'):
                 raise PermissionDenied("You must be an Admin to create users with this role.")

        serializer.save()


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
