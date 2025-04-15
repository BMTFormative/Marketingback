#!/usr/bin/env python
"""
Script to run the Django development server on a specific port.
This script bypasses normal Django management commands to allow more flexibility.
"""
import os
import sys
import subprocess

def main():
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Set up Django environment
    import django
    django.setup()
    
    # Create directories if they don't exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('media', exist_ok=True)
    os.makedirs('staticfiles', exist_ok=True)
    
    # Run migrations
    print("Running migrations...")
    from django.core.management import call_command
    call_command('makemigrations', 'api')
    call_command('migrate')
    
    # Create a superuser if none exists
    from django.contrib.auth.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
        
    # Create user profile for superuser if it doesn't exist
    from api.models import UserProfile
    admin_user = User.objects.get(username='admin')
    if not hasattr(admin_user, 'userprofile'):
        print("Creating admin user profile...")
        UserProfile.objects.create(user=admin_user, role='admin')
    
    # Start the development server
    print("Starting Django development server on port 8000...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

if __name__ == "__main__":
    main()