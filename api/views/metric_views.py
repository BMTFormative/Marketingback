from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from django.db.models import Sum, Avg, Max, Min, Count
from django.utils import timezone

from ..models import MarketingMetric, CsvUpload
from ..serializers import MarketingMetricSerializer
from ..permissions import IsOwnerOrAdmin


class MarketingMetricViewSet(viewsets.ModelViewSet):
    """
    API view for marketing metrics
    """
    serializer_class = MarketingMetricSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Return metrics owned by the current user or all metrics for admin
        """
        user = self.request.user
        if user.userprofile.role == 'admin':
            return MarketingMetric.objects.all()
        return MarketingMetric.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def by_csv_upload(self, request):
        """
        Get metrics filtered by csv_upload_id
        """
        csv_upload_id = request.query_params.get('csv_upload_id')
        if not csv_upload_id:
            return Response(
                {'error': 'csv_upload_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Check if CSV upload exists and is owned by user
            csv_upload = CsvUpload.objects.get(id=csv_upload_id)
            if csv_upload.user != request.user and request.user.userprofile.role != 'admin':
                return Response(
                    {'error': 'You do not have permission to access this data'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Get metrics for this CSV upload
            queryset = self.get_queryset().filter(csv_upload_id=csv_upload_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except CsvUpload.DoesNotExist:
            return Response(
                {'error': 'CSV upload not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary metrics for the current user
        """
        queryset = self.get_queryset()
        
        # Apply date range filter if specified
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Get aggregate metrics
        aggregates = queryset.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_conversions=Sum('conversions'),
            total_cost=Sum('cost'),
            total_revenue=Sum('revenue'),
            avg_ctr=Avg('click_through_rate'),
            avg_cvr=Avg('conversion_rate'),
            avg_roi=Avg('roi'),
            avg_cpc=Avg('average_cpc'),
            metric_count=Count('id')
        )
        
        # Calculate derived metrics
        if aggregates['total_impressions'] and aggregates['total_clicks']:
            overall_ctr = (aggregates['total_clicks'] / aggregates['total_impressions']) * 100
        else:
            overall_ctr = 0
            
        if aggregates['total_clicks'] and aggregates['total_conversions']:
            overall_cvr = (aggregates['total_conversions'] / aggregates['total_clicks']) * 100
        else:
            overall_cvr = 0
            
        if aggregates['total_cost'] and aggregates['total_revenue']:
            overall_roi = ((aggregates['total_revenue'] - aggregates['total_cost']) / aggregates['total_cost']) * 100
        else:
            overall_roi = 0
            
        if aggregates['total_clicks'] and aggregates['total_cost']:
            overall_cpc = aggregates['total_cost'] / aggregates['total_clicks']
        else:
            overall_cpc = 0
            
        # Prepare response
        response_data = {
            'metrics_count': aggregates['metric_count'] or 0,
            'total_impressions': aggregates['total_impressions'] or 0,
            'total_clicks': aggregates['total_clicks'] or 0,
            'total_conversions': aggregates['total_conversions'] or 0,
            'total_cost': float(aggregates['total_cost'] or 0),
            'total_revenue': float(aggregates['total_revenue'] or 0),
            'overall_ctr': round(overall_ctr, 2),
            'overall_cvr': round(overall_cvr, 2),
            'overall_roi': round(overall_roi, 2),
            'overall_cpc': round(float(overall_cpc), 2),
            'average_ctr': round(float(aggregates['avg_ctr'] or 0), 2),
            'average_cvr': round(float(aggregates['avg_cvr'] or 0), 2),
            'average_roi': round(float(aggregates['avg_roi'] or 0), 2),
            'average_cpc': round(float(aggregates['avg_cpc'] or 0), 2),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return Response(response_data)
        
    @action(detail=False, methods=['get'])
    def platforms(self, request):
        """
        Get metrics grouped by platform
        """
        queryset = self.get_queryset()
        platforms = queryset.values('platform').distinct()
        
        platform_data = []
        for platform_dict in platforms:
            platform = platform_dict['platform']
            if not platform:  # Skip empty platforms
                continue
                
            platform_metrics = queryset.filter(platform=platform)
            
            # Get aggregates for this platform
            aggregates = platform_metrics.aggregate(
                total_impressions=Sum('impressions'),
                total_clicks=Sum('clicks'),
                total_conversions=Sum('conversions'),
                total_cost=Sum('cost'),
                total_revenue=Sum('revenue'),
                metric_count=Count('id')
            )
            
            # Calculate derived metrics
            if aggregates['total_impressions'] and aggregates['total_clicks']:
                platform_ctr = (aggregates['total_clicks'] / aggregates['total_impressions']) * 100
            else:
                platform_ctr = 0
                
            if aggregates['total_clicks'] and aggregates['total_conversions']:
                platform_cvr = (aggregates['total_conversions'] / aggregates['total_clicks']) * 100
            else:
                platform_cvr = 0
                
            if aggregates['total_cost'] and aggregates['total_revenue']:
                platform_roi = ((aggregates['total_revenue'] - aggregates['total_cost']) / aggregates['total_cost']) * 100
            else:
                platform_roi = 0
                
            platform_data.append({
                'platform': platform,
                'metrics_count': aggregates['metric_count'] or 0,
                'impressions': aggregates['total_impressions'] or 0,
                'clicks': aggregates['total_clicks'] or 0,
                'conversions': aggregates['total_conversions'] or 0,
                'cost': float(aggregates['total_cost'] or 0),
                'revenue': float(aggregates['total_revenue'] or 0),
                'ctr': round(platform_ctr, 2),
                'cvr': round(platform_cvr, 2),
                'roi': round(platform_roi, 2)
            })
            
        return Response(platform_data)


class CalculateMetricsView(APIView):
    """
    API view for calculating metrics for a specific dataset
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get parameters
        csv_upload_id = request.data.get('csv_upload_id')
        platform = request.data.get('platform')
        date_range = request.data.get('date_range', {})
        
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
            return Response({
                'conversionRate': 0,
                'clickThroughRate': 0,
                'roi': 0,
                'averageCpc': 0
            })
            
        # Calculate metrics
        aggregates = queryset.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_conversions=Sum('conversions'),
            total_cost=Sum('cost'),
            total_revenue=Sum('revenue')
        )
        
        # Calculate derived metrics
        if aggregates['total_impressions'] and aggregates['total_clicks']:
            ctr = (aggregates['total_clicks'] / aggregates['total_impressions']) * 100
        else:
            ctr = 0
            
        if aggregates['total_clicks'] and aggregates['total_conversions']:
            cvr = (aggregates['total_conversions'] / aggregates['total_clicks']) * 100
        else:
            cvr = 0
            
        if aggregates['total_cost'] and aggregates['total_revenue']:
            roi = ((aggregates['total_revenue'] - aggregates['total_cost']) / aggregates['total_cost']) * 100
        else:
            roi = 0
            
        if aggregates['total_clicks'] and aggregates['total_cost']:
            cpc = aggregates['total_cost'] / aggregates['total_clicks']
        else:
            cpc = 0
            
        return Response({
            'conversionRate': round(cvr, 2),
            'clickThroughRate': round(ctr, 2),
            'roi': round(roi, 2),
            'averageCpc': round(float(cpc), 2)
        })