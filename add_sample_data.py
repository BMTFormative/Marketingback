#!/usr/bin/env python
"""
Script to add sample data to the Django database.
"""
import os
import sys
from datetime import date, timedelta

def main():
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Set up Django environment
    import django
    django.setup()
    
    # Import models
    from django.contrib.auth.models import User
    from api.models import Campaign, CsvUpload, MarketingMetric, AiInsight
    
    # Get admin user (created during migrations)
    admin_user = User.objects.get(username='admin')
    
    # Add a sample campaign
    campaign = Campaign.objects.create(
        name="Sample Facebook Campaign",
        description="This is a sample campaign for testing",
        user=admin_user,
        status="active",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        budget=1000.00,
        target_audience="Adults 25-40",
        platform="Facebook"
    )
    print(f"Created campaign: {campaign.name}")
    
    # Add a sample AI insight
    insight = AiInsight.objects.create(
        user=admin_user,
        title="Performance Improving",
        content="The campaign performance is showing a positive trend with increasing ROI over the past week.",
        category="performance"
    )
    print(f"Created insight: {insight.title}")
    
    # Print summary
    print("\nSample data has been added to the database.")
    print(f"Campaigns: {Campaign.objects.count()}")
    print(f"Insights: {AiInsight.objects.count()}")

if __name__ == "__main__":
    main()