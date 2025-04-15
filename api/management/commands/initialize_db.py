from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile, Campaign
from django.utils import timezone
import os
import datetime

class Command(BaseCommand):
    help = 'Initialize the database with admin user and sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database initialization'))
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='password123',
                first_name='Admin',
                last_name='User'
            )
            
            # Update profile
            profile = UserProfile.objects.get(user=admin_user)
            profile.role = 'admin'
            profile.status = 'active'
            profile.last_login = timezone.now()
            profile.save()
            
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))
        
        # Create sample client user
        if not User.objects.filter(username='client').exists():
            client_user = User.objects.create_user(
                username='client',
                email='client@example.com',
                password='password123',
                first_name='Client',
                last_name='User'
            )
            
            # Update profile
            profile = UserProfile.objects.get(user=client_user)
            profile.role = 'client'
            profile.status = 'active'
            profile.last_login = timezone.now()
            profile.save()
            
            self.stdout.write(self.style.SUCCESS('Client user created'))
        else:
            self.stdout.write(self.style.SUCCESS('Client user already exists'))
        
        # Create sample campaigns if none exist
        if Campaign.objects.count() == 0:
            admin = User.objects.get(username='admin')
            client = User.objects.get(username='client')
            
            # Create campaigns for admin
            Campaign.objects.create(
                name='Q1 2025 Digital Marketing',
                user=admin,
                status='active',
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 3, 31),
                budget=10000.00,
                description='First quarter digital marketing campaign focused on increasing brand awareness.'
            )
            
            # Create campaigns for client
            Campaign.objects.create(
                name='Summer Promotion 2025',
                user=client,
                status='active',
                start_date=datetime.date(2025, 6, 1),
                end_date=datetime.date(2025, 8, 31),
                budget=7500.00,
                description='Summer promotion focusing on new product launches.'
            )
            
            self.stdout.write(self.style.SUCCESS('Sample campaigns created'))
        else:
            self.stdout.write(self.style.SUCCESS('Campaigns already exist'))
        
        self.stdout.write(self.style.SUCCESS('Database initialization complete!'))