from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Marketing Analytics API'
    
    def ready(self):
        """Register signals when the app is ready"""
        import api.signals
