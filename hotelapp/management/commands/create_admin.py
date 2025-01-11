from django.core.management.base import BaseCommand
from hotelapp.models import CustomUser

class Command(BaseCommand):
    help = 'Creates a superuser with admin user type'

    def handle(self, *args, **options):
        try:
            admin = CustomUser.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='your_password',
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created superuser'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}')) 