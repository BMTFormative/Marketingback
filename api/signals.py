"""
Signal handlers for the API app
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
import os

from .models import UserProfile, CsvUpload

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile instance when a User is created
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(pre_delete, sender=CsvUpload)
def delete_csv_file(sender, instance, **kwargs):
    """
    Delete the associated CSV file when a CsvUpload is deleted
    """
    if instance.file_path and os.path.exists(instance.file_path):
        try:
            os.remove(instance.file_path)
        except Exception as e:
            # Log the error but don't prevent deletion
            print(f"Error deleting file {instance.file_path}: {str(e)}")