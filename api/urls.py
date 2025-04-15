from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import authentication views
from .authentication import LoginView, LogoutView, RegisterView, CurrentUserView

# Import viewsets directly from their respective files
from .views.user_views import UserViewSet
from .views.campaign_views import CampaignViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'campaigns', CampaignViewSet, basename='campaign')

# Uncomment these as you implement each viewset
# router.register(r'csv-uploads', CsvUploadViewSet, basename='csv-upload')
# router.register(r'metrics', MarketingMetricViewSet, basename='metric')
# router.register(r'insights', AiInsightViewSet, basename='insight')
# router.register(r'api-configurations', ApiConfigurationViewSet, basename='api-configuration')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', CurrentUserView.as_view(), name='current-user'),
    
    # Include DRF auth URLs (for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='api-rest-framework')),
]