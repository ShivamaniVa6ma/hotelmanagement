from django.core.management.base import BaseCommand
from hotelapp.models import CustomUser, Profile

class Command(BaseCommand):
    help = 'Create profiles for all existing users'

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()
        for user in users:
            Profile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created profiles for all users.')) 