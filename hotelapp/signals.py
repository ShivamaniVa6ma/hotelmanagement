from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile
from django.utils import timezone
import uuid

@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

# Update the profile when the reset token is created
def set_reset_token(user):
    profile, created = Profile.objects.get_or_create(user=user)
    profile.reset_token = str(uuid.uuid4())
    profile.reset_token_created_at = timezone.now()  # Set the current time
    profile.save() 