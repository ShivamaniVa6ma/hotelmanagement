from django.db import models
from subscription.models import SubscriptionUserDetails
# Create your models here.

class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

class UserMap(models.Model):
    subscription_user = models.OneToOneField(SubscriptionUserDetails, on_delete=models.CASCADE, related_name='user_map')
    embed_code = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
