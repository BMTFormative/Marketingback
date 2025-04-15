from django.utils import timezone
from datetime import timedelta
from .models import UserProfile

class UpdateLastActivityMiddleware:
    """
    Middleware to update the user's last activity timestamp
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Update the user's last activity time if authenticated
        if request.user.is_authenticated:
            try:
                # Only update the last_login field once per hour to avoid excessive writes
                profile = UserProfile.objects.get(user=request.user)
                last_login = profile.last_login
                
                if not last_login or timezone.now() > last_login + timedelta(hours=1):
                    profile.last_login = timezone.now()
                    profile.save(update_fields=['last_login'])
            except UserProfile.DoesNotExist:
                pass
                
        return response