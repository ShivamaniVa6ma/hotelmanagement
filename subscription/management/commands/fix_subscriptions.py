from django.core.management.base import BaseCommand
from subscription.models import SubscriptionUserDetails, Cart

class Command(BaseCommand):
    help = 'Fix subscription relationships'

    def handle(self, *args, **kwargs):
        for user_detail in SubscriptionUserDetails.objects.filter(subscription_plan__isnull=True):
            cart = Cart.objects.filter(user_details=user_detail).order_by('-created_at').first()
            if cart and cart.plan:
                user_detail.subscription_plan = cart.plan
                user_detail.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated subscription plan for {user_detail.name} to {cart.plan.name}'
                    )
                ) 