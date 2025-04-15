from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from .serializers import UserSerializer, UserRegistrationSerializer

class RegisterView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
                            
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            return Response(UserSerializer(user).data)
        
        return Response({'error': 'Invalid credentials'},
                        status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    """
    API endpoint to get current authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)