from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import viewsets
from .views.user_views import UserViewSet
from .views.campaign_views import CampaignViewSet
from .views.metric_views import MarketingMetricViewSet, CalculateMetricsView
from .views.insight_views import AiInsightViewSet, GenerateInsightsView
from .views.api_config_views import ApiConfigurationViewSet
from .views.csv_views import UploadCsvView, ProcessCsvView
from .authentication import LoginView, LogoutView, RegisterView, CurrentUserView

# Create a debug view to verify URL routing
@api_view(['GET'])
def debug_view(request):
    routes = [
        {'path': '/api/users/', 'methods': ['GET', 'POST'], 'name': 'user-list'},
        {'path': '/api/campaigns/', 'methods': ['GET', 'POST'], 'name': 'campaign-list'},
        {'path': '/api/metrics/', 'methods': ['GET', 'POST'], 'name': 'metric-list'},
        {'path': '/api/insights/', 'methods': ['GET', 'POST'], 'name': 'insight-list'},
        {'path': '/api/api-configurations/', 'methods': ['GET', 'POST'], 'name': 'api-configuration-list'},
    ]
    return Response(routes)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'metrics', MarketingMetricViewSet, basename='metric')
router.register(r'insights', AiInsightViewSet, basename='insight')
router.register(r'api-configurations', ApiConfigurationViewSet, basename='api-configuration')

urlpatterns = [
    # Debug route
    path('debug/', debug_view, name='debug'),
    
    # Authentication URLs
    path('login', LoginView.as_view(), name='login-no-slash'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout-no-slash'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register', RegisterView.as_view(), name='register-no-slash'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user', CurrentUserView.as_view(), name='current-user-no-slash'),
    path('user/', CurrentUserView.as_view(), name='current-user'),
    
    # Add API view paths (non-ModelViewSets)
    path('upload-csv', UploadCsvView.as_view(), name='upload-csv'),
    path('upload-csv/', UploadCsvView.as_view(), name='upload-csv-slash'),
    path('process-csv/<int:pk>', ProcessCsvView.as_view(), name='process-csv'),
    path('process-csv/<int:pk>/', ProcessCsvView.as_view(), name='process-csv-slash'),
    path('delete-csv/<int:pk>', UploadCsvView.as_view(), name='delete-csv'),
    path('delete-csv/<int:pk>/', UploadCsvView.as_view(), name='delete-csv-slash'),
    path('calculate-metrics', CalculateMetricsView.as_view(), name='calculate-metrics'),
    path('calculate-metrics/', CalculateMetricsView.as_view(), name='calculate-metrics-slash'),
    path('generate-insights', GenerateInsightsView.as_view(), name='generate-insights'),
    path('generate-insights/', GenerateInsightsView.as_view(), name='generate-insights-slash'),
    
    # Include router URLs - try explicitly adding them
    path('', include(router.urls)),
    
    # Include DRF auth URLs (for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='api-rest-framework')),
]