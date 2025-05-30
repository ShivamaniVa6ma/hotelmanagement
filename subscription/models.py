from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
import secrets

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    #features = models.JSONField(default=list)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_free_trial=models.BooleanField(default=False)
    is_logo_change = models.BooleanField(default=False)
    
    # Feature limitations (these are already in your database)
    max_rooms = models.IntegerField(default='')
    max_bookings_per_month = models.IntegerField(default='')
    max_team_members = models.IntegerField(default='')
    allow_analytics = models.BooleanField(default=False)
    allow_advanced_reports = models.BooleanField(default=False)
    allow_api_access = models.BooleanField(default=False)
    
    # total_rooms = models.IntegerField(default='',blank= True, null=True)
    # team_members = models.IntegerField(default='',blank= True, null=True)
    # total_bookings_per_month = models.IntegerField(default='',blank= True, null=True)
    
    def __str__(self):
        return self.name

    def get_discounted_price(self, duration_months):
        discount = self.discounts.filter(duration_months=duration_months).first()
        if discount:
            return self.monthly_price * (1 - discount.discount_percentage / 100)
        return self.monthly_price

    def get_total_price(self, duration_months):
        return self.get_discounted_price(duration_months) * duration_months

    def get_active_features(self):
        return self.plan_features.filter(is_active=True)

    def get_feature_list(self):
        features = []
        if self.allow_analytics:
            features.append("Analytics Dashboard")
        if self.allow_advanced_reports:
            features.append("Advanced Reports")
        if self.allow_api_access:
            features.append("API Access")
        features.extend([
            f"Up to {self.max_rooms} Rooms",
            f"Up to {self.max_bookings_per_month} Bookings/Month",
            f"Up to {self.max_team_members} Team Members"
        ])
        return features

    class Meta:
        ordering = ['monthly_price']

class SubscriptionDiscount(models.Model):
    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
        (24, '24 Months'),
        (48, '48 Months'),
    ]
    
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='discounts')
    duration_months = models.IntegerField(choices=DURATION_CHOICES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        unique_together = ['subscription_plan', 'duration_months']
        ordering = ['duration_months']

    def __str__(self):
        return f"{self.get_duration_months_display()} - {self.discount_percentage}% off"

class PlanFeature(models.Model):
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.CASCADE, 
        related_name='plan_features',
        null=True,
        blank=True
    )
    feature_text = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.feature_text

    class Meta:
        ordering = ['created_at']


class SubscriptionUserDetails(models.Model):
    booking_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    company_name = models.CharField(max_length=100)
    address = models.TextField()
    secret_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    is_key_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscription_user_details'
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptionuserdetails'
    )

    class Meta:
        indexes = [
            models.Index(fields=['email', 'is_active'])
        ]
        unique_together = ['email', 'is_active']

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BOOK_{uuid.uuid4().hex[:8].upper()}"
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
        
        if self.is_active and not self.pk:
            SubscriptionUserDetails.objects.filter(
                email=self.email,
                is_active=True
            ).update(is_active=False)
            
        super().save(*args, **kwargs)

    def is_subscription_active(self):
        """Check if subscription is active and not expired"""
        if not self.is_active:
            return False
        if self.subscription_end_date and self.subscription_end_date < timezone.now():
            self.is_active = False
            self.save()
            return False
        return True

    def mark_key_as_used(self):
        """Mark key as used and ensure subscription end date is set"""
        self.is_key_used = True
        if not self.subscription_end_date:
            # Set default subscription period if not set (e.g., 30 days)
            self.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
        self.save()
    
    def save(self, *args, **kwargs):
        # Normalize the company name for URL usage
        self.company_name = self.company_name.lower().replace(' ', '-')
        super(SubscriptionUserDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.company_name} - {self.name}"

class Cart(models.Model):
    user_details = models.ForeignKey(SubscriptionUserDetails, on_delete=models.CASCADE, null=True, blank=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    duration_months = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return self.plan.get_total_price(self.duration_months)

    def get_discount_percentage(self):
        discount = self.plan.discounts.filter(duration_months=self.duration_months).first()
        return discount.discount_percentage if discount else 0


class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )
   
    id = models.AutoField(primary_key=True)
    user_details = models.ForeignKey(SubscriptionUserDetails, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Stores Razorpay order ID
    razorpay_payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Stores actual payment ID
    order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Our internal order ID
    invoice_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_id} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)

    def generate_invoice_id(self):
        return f"INV-{uuid.uuid4().hex[:8].upper()}"  # Example: INV-A1B2C3D4
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} - {self.email}"
    

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_platform_fee = models.BooleanField(default=False)  # NEW FIELD

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.percentage}%"
    



