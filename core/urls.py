"""
URL configuration for Marketing Analytics Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.authentication import LoginView, LogoutView, RegisterView, CurrentUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user/', CurrentUserView.as_view(), name='current_user'),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # DRF built-in auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
