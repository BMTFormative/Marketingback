#!/usr/bin/env python
"""
Script to verify Django ORM and model functionality.
"""
import os
import sys
import json

def main():
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Set up Django environment
    import django
    django.setup()
    
    # Import models
    from django.contrib.auth.models import User
    from api.models import UserProfile, Campaign, CsvUpload, MarketingMetric, AiInsight, ApiConfiguration
    
    # Count records in each model
    user_count = User.objects.count()
    profile_count = UserProfile.objects.count()
    campaign_count = Campaign.objects.count()
    csv_count = CsvUpload.objects.count()
    metric_count = MarketingMetric.objects.count()
    insight_count = AiInsight.objects.count()
    config_count = ApiConfiguration.objects.count()
    
    # Print record counts
    print(json.dumps({
        "database_connection": "success",
        "models": {
            "User": user_count,
            "UserProfile": profile_count,
            "Campaign": campaign_count,
            "CsvUpload": csv_count,
            "MarketingMetric": metric_count,
            "AiInsight": insight_count,
            "ApiConfiguration": config_count
        },
        "database_url": os.environ.get('DATABASE_URL', 'Not set')[:20] + '...' if os.environ.get('DATABASE_URL') else 'Not set'
    }, indent=2))
    
    # Check for admin user
    admin_exists = User.objects.filter(username='admin').exists()
    if not admin_exists:
        print("Creating admin user...")
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
        UserProfile.objects.create(user=admin_user, role='admin')
    else:
        print("Admin user already exists.")
        admin_user = User.objects.get(username='admin')
        if not hasattr(admin_user, 'userprofile'):
            print("Creating admin user profile...")
            UserProfile.objects.create(user=admin_user, role='admin')

if __name__ == "__main__":
    main()