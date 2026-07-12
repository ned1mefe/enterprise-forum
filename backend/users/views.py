"""
User views for authentication and profile management.

Views remain thin — business logic stays in services/serializers (§16).
"""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin
from .serializers import UserCreateSerializer, UserSerializer


class LoginView(APIView):
    """
    POST /api/auth/login/

    Authenticate user and return JWT token pair.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Username and password are required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "authentication_failed",
                        "message": "Invalid credentials.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {
                    "error": {
                        "code": "authentication_failed",
                        "message": "Invalid credentials.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {
                    "error": {
                        "code": "authentication_failed",
                        "message": "This account is inactive.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    GET /api/auth/profile/

    Return the authenticated user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/auth/users/     — List all users (admin only).
    POST /api/auth/users/     — Create a new user (admin only).
    """

    permission_classes = [IsAdmin]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/users/{id}/    — Get user details (admin only).
    PUT /api/auth/users/{id}/    — Update user (admin only).
    """

    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer
