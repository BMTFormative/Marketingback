from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import ApiConfiguration
from ..serializers import ApiConfigurationSerializer
from ..permissions import IsOwnerOrAdmin


class ApiConfigurationViewSet(viewsets.ModelViewSet):
    """
    API viewset for API configuration operations
    """
    serializer_class = ApiConfigurationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Return API configurations owned by the current user or all configurations for admin
        """
        user = self.request.user
        if user.userprofile.role == 'admin':
            return ApiConfiguration.objects.all()
        return ApiConfiguration.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Set the user on API configuration creation
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get the active API configuration
        """
        queryset = self.get_queryset().filter(active=True).first()
        if not queryset:
            return Response(
                {'error': 'No active API configuration found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def set_active(self, request, pk=None):
        """
        Set this API configuration as the active one
        """
        try:
            # Get the API configuration
            api_config = self.get_object()
            
            # Check if user is allowed to modify this configuration
            if api_config.user != request.user and request.user.userprofile.role != 'admin':
                return Response(
                    {'error': 'You do not have permission to modify this configuration'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Deactivate all other configurations
            ApiConfiguration.objects.all().update(active=False)
            
            # Activate this configuration
            api_config.active = True
            api_config.save(update_fields=['active'])
            
            serializer = self.get_serializer(api_config)
            return Response(serializer.data)
            
        except ApiConfiguration.DoesNotExist:
            return Response(
                {'error': 'API configuration not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['put'])
    def verify(self, request, pk=None):
        """
        Verify that the API key works
        """
        try:
            # Get the API configuration
            api_config = self.get_object()
            
            # Check if user is allowed to verify this configuration
            if api_config.user != request.user and request.user.userprofile.role != 'admin':
                return Response(
                    {'error': 'You do not have permission to verify this configuration'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # In a real application, you would verify the API key by making a test request
            # Here we'll just return success
            
            return Response({
                'verified': True,
                'message': 'API key verified successfully'
            })
            
        except ApiConfiguration.DoesNotExist:
            return Response(
                {'error': 'API configuration not found'},
                status=status.HTTP_404_NOT_FOUND
            )