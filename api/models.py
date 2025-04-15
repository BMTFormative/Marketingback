from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """
    Extended user profile linked to the Django User model
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expiration_date = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Campaign(models.Model):
    """
    Marketing campaign details
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class CsvUpload(models.Model):
    """
    CSV Upload metadata
    """
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='csv_uploads')
    processed = models.BooleanField(default=False)
    row_count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.filename


class MarketingMetric(models.Model):
    """
    Marketing metrics derived from CSV data
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketing_metrics')
    csv_upload = models.ForeignKey(CsvUpload, on_delete=models.CASCADE, related_name='metrics', null=True, blank=True)
    platform = models.CharField(max_length=50)
    date = models.DateField()
    campaign_name = models.CharField(max_length=100)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    roi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ctr = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_click = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_conversion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.platform} - {self.campaign_name} - {self.date}"


class AiInsight(models.Model):
    """
    AI-generated insights from marketing data
    """
    CATEGORY_CHOICES = (
        ('performance', 'Performance'),
        ('trend', 'Trend'),
        ('recommendation', 'Recommendation'),
        ('alert', 'Alert'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class ApiConfiguration(models.Model):
    """
    API configuration for external services
    """
    SERVICE_TYPE_CHOICES = (
        ('openai', 'OpenAI'),
        ('google_analytics', 'Google Analytics'),
        ('facebook_ads', 'Facebook Ads'),
        ('google_ads', 'Google Ads'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_configurations')
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255, blank=True, null=True)
    additional_params = models.JSONField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.service_type}"