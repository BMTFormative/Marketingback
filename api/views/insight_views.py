from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from django.utils import timezone

from ..models import AiInsight, MarketingMetric, ApiConfiguration
from ..serializers import AiInsightSerializer
from ..permissions import IsOwnerOrAdmin
from ..services import generate_ai_insights


class AiInsightViewSet(viewsets.ModelViewSet):
    """
    API view for AI insights
    """
    serializer_class = AiInsightSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Return insights owned by the current user or all insights for admin
        """
        user = self.request.user
        if user.userprofile.role == 'admin':
            return AiInsight.objects.all()
        return AiInsight.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get insights filtered by category
        """
        category = request.query_params.get('category')
        if not category:
            return Response(
                {'error': 'category parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        queryset = self.get_queryset().filter(category=category)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GenerateInsightsView(APIView):
    """
    API view for generating AI insights from metrics
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get parameters
        csv_upload_id = request.data.get('csv_upload_id')
        platform = request.data.get('platform')
        date_range = request.data.get('date_range', {})
        
        # Check if there's an active API configuration
        api_config = ApiConfiguration.objects.filter(active=True).first()
        if not api_config:
            return Response(
                {'error': 'No active AI API configuration found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get metrics to analyze
        queryset = MarketingMetric.objects.filter(user=request.user)
        
        # Apply filters
        if csv_upload_id:
            queryset = queryset.filter(csv_upload_id=csv_upload_id)
            
        if platform:
            queryset = queryset.filter(platform=platform)
            
        if date_range.get('start_date'):
            queryset = queryset.filter(date__gte=date_range['start_date'])
            
        if date_range.get('end_date'):
            queryset = queryset.filter(date__lte=date_range['end_date'])
            
        # If no metrics match the criteria
        if not queryset.exists():
            return Response(
                {'error': 'No metrics found matching the specified criteria'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Generate insights
        success, message = generate_ai_insights(queryset, request.user.id)
        
        if success:
            # Get the newly created insights
            insights = AiInsight.objects.filter(
                user=request.user,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
            ).order_by('-created_at')
            
            serializer = AiInsightSerializer(insights, many=True)
            return Response({
                'message': message,
                'insights': serializer.data
            })
        else:
            return Response(
                {'error': message}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )