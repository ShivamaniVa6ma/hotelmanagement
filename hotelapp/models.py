from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from subscription.models import SubscriptionUserDetails,SubscriptionPlan
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class CustomUser(AbstractUser):
    # Remove PermissionsMixin since it's already included in AbstractUser
    subscription = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscribers'
    )
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    is_subscription_active = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)

    class Meta:
        db_table = 'hotelapp_customuser'
        permissions = [
            ("can_view_dashboard", "Can view dashboard"),
            ("can_access_premium_features", "Can access premium features"),
        ]

    def check_subscription_status(self):
        if not self.subscription or not self.subscription_end_date:
            return False
        return timezone.now() <= self.subscription_end_date

    def get_available_features(self):
        if not self.subscription:
            return []
        return self.subscription.plan_features.filter(is_active=True)

    def __str__(self):
        return self.username
    

# Now import SubscriptionUserDetails

class Room(models.Model):
    
    
    BED_TYPE_CHOICES = [
        ('single', 'Single Bed'),
        ('double', 'Double Bed'),
        ('king', 'King Bed'),
        ('queen', 'Queen Bed'),
    ]
    
    AC_CHOICES = [
        ('ac', 'AC'),
        ('nonAc', 'Non-AC'),
    ]
    
    room_number = models.CharField(max_length=10)
    block = models.CharField(max_length=50, default='')
    
    bed_type = models.CharField(max_length=10, choices=BED_TYPE_CHOICES, null=True, blank=True)
    ac_type = models.CharField(max_length=5, choices=AC_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    weekend_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    holiday_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    hourly_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    max_occupancy = models.IntegerField()
    seating_capacity = models.IntegerField(null=True, blank=True)
    features = models.ManyToManyField('Feature', blank=True)  # ✅ Correct ManyToManyField
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)  # Added this field
    subscription_plan = models.ForeignKey(SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='rooms'
    )
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        related_name='rooms',
        null=True,
        blank=True
    )
    room_type = models.ForeignKey(
        'RoomType',
        on_delete=models.CASCADE,  # ✅ If RoomType is deleted, Room should also get deleted
        related_name='rooms'
    )

    def save_images(self, images):
        """
        Save multiple images for the room
        """
        for image in images:
            RoomImage.objects.create(room=self, image=image)

    def __str__(self):
        return f"{self.room_type} - Room {self.room_number}"

    class Meta:
        unique_together = [
            ('room_number', 'block', 'subscription_user')
        ]


class RoomType(models.Model):
    BED_TYPE_CHOICES = [
            ('bed type', 'Bed Type'),
            ('conference', 'Conference'),
        ]

    name = models.CharField(max_length=100)
    available_from = models.DateTimeField(blank=True,null=True)  # New DateTimeField
    bed_type = models.CharField(max_length=10, choices=BED_TYPE_CHOICES, default='bed type')
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name
        
class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_images/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        related_name='room_images',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Image for Room {self.room.room_number}"
    
class Feature(models.Model):
    name = models.CharField(max_length=255)
    
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='feature_images/', blank=True, null=True)
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

class Guest(models.Model):
    PROOF_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('pan', 'Pan Card'),
        ('aadhar', 'Aadhar Card'),
        ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='guest_profile')  # Link to CustomUser
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    proof_type = models.CharField(max_length=20, choices=PROOF_TYPE_CHOICES)
    proof_no = models.CharField(max_length=50)
    proof_file = models.FileField(upload_to='proof_files/', blank=True, null=True)  # New field
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        related_name='guests',
        null=True,
        blank=True
    )
    profile_picture = models.ImageField(upload_to='guest_profiles/', blank=True, null=True)

    
    def __str__(self):
        return self.name

class Booking(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('razorpay','Razorpay'),
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]
    
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    adults = models.IntegerField()
    children = models.IntegerField(default=0)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='razorpay')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')

    # for online payment
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)  # NEW
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')  # NEW
    invoice_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        related_name='bookings',
        blank=True,
        null=True,
    )


    
    
    def __str__(self):
        return f"Booking for {self.guest.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class TeamMember(models.Model):
    image = models.ImageField(upload_to='team_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    email1 = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, blank=True, null=True)
    address1 = models.TextField()
    address2 = models.TextField(blank=True, null=True)  
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    github = models.CharField(max_length=100, blank=True, null=True)
    designation = models.ForeignKey('TeamDesignation', on_delete=models.CASCADE, null=True, blank=True)  # Foreign key to TeamDesignation
    aadhar_no = models.CharField(max_length=12, null=True, blank=True)
    pan_no = models.CharField(max_length=10, blank=True, null=True)
    aadhar_file = models.FileField(upload_to='aadhar_files/', blank=True, null=True)
    pan_file = models.FileField(upload_to='pan_files/', blank=True, null=True)
    subscription_user = models.ForeignKey(
        'subscription.SubscriptionUserDetails',
        on_delete=models.CASCADE,
        related_name='team_members',
        null=True,
        blank=True
    )

    class Meta:
        unique_together = (
            ('subscription_user', 'email1'),
            ('subscription_user', 'phone1'),
            ('subscription_user', 'account_name'),
            ('subscription_user', 'account_number'),
            ('subscription_user', 'aadhar_no'),
            ('subscription_user', 'pan_no'),
        )

    def __str__(self):
        return self.name

    def belongs_to_subscription(self, subscription_id):
        return self.subscription_user_id == subscription_id
    

class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)  # e.g., Breakfast, Lunch, Dinner
    status = models.CharField(max_length=20)  # e.g., Available, Not Available
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='food_images/')  # Ensure you have Pillow installed
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        related_name='food_items',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_created_at = models.DateTimeField(blank=True, null=True)  # New field
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        related_name='profiles',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
    

# Signal to create a Profile when a CustomUser is created
@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    




class LogoSettings(models.Model):
    site_name = models.CharField(max_length=255)
    favicon = models.ImageField(
        upload_to='logos/favicons/', blank=True, null=True, 
        default='assets/img/logo/logo-3.png'
        )

    light_logo = models.ImageField(
        upload_to='logos/light/', blank=True, null=True, 
        default='assets/img/logo/collapse-logo.png')
    dark_logo = models.ImageField(
        upload_to='logos/dark/', blank=True, null=True, 
        default='assets/img/logo/full-logo.png')

    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.site_name

class TeamDesignation(models.Model):
    designation = models.CharField(max_length=255)
    date_time = models.DateTimeField(blank=True,null=True)

    subscription_user = models.ForeignKey( 
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.designation} - {self.subscription_user.user.username if self.subscription_user else 'No User'}"

class Event(models.Model):
    occasion = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


    def __str__(self):
        return self.occasion

class Facility(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.FileField(upload_to='facilities/images/', null=True, blank=True)
    icon = models.FileField(upload_to='facilities/icons/', null=True, blank=True)
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - Subscription User: {self.subscription_user_id}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class Spa(models.Model):
    name = models.CharField(max_length=255)
    from_time = models.TimeField()
    to_time = models.TimeField()
    description = models.TextField()
    image = models.ImageField(upload_to='spa/images/', null=True, blank=True)
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AboutUs(models.Model):
    image = models.FileField(upload_to='about_us/images/', null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    subscription_user = models.ForeignKey(
            SubscriptionUserDetails,
            on_delete=models.CASCADE,
            null=True,
            blank=True
        )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # 👈 Add this if not present

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.FileField(upload_to='services/icons/', null=True, blank=True)
    image = models.FileField(upload_to='services/images/', null=True, blank=True)
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription_user = models.ForeignKey(
        SubscriptionUserDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.percentage}%"
    

    