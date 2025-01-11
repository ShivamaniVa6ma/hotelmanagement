from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('vip', 'VIP Room'),
        ('conference', 'Conference Room'),
    ]
    
    BED_TYPE_CHOICES = [
        ('single', 'Single Bed'),
        ('double', 'Double Bed'),
    ]
    
    AC_CHOICES = [
        ('ac', 'AC'),
        ('nonAc', 'Non-AC'),
    ]
    
    room_number = models.CharField(max_length=10, unique=True)
    block = models.CharField(max_length=50,default='')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    bed_type = models.CharField(max_length=10, choices=BED_TYPE_CHOICES, null=True, blank=True)
    ac_type = models.CharField(max_length=5, choices=AC_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    weekend_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    holiday_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    hourly_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    max_occupancy = models.IntegerField()
    seating_capacity = models.IntegerField(null=True, blank=True)
    features = models.JSONField(default=list)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)  # Added this field

    def save_images(self, images):
        """
        Save multiple images for the room
        """
        for image in images:
            RoomImage.objects.create(room=self, image=image)

    def __str__(self):
        return f"{self.room_type} - Room {self.room_number}"

class RoomImage(models.Model):
    room = models.ForeignKey('Room', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_images/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Image for Room {self.room.room_number}"

class Guest(models.Model):
    PROOF_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('pan', 'Pan Card'),
        ('aadhar', 'Aadhar Card'),
        ]
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    proof_type = models.CharField(max_length=20, choices=PROOF_TYPE_CHOICES)
    proof_no = models.CharField(max_length=50)
    proof_file = models.FileField(upload_to='proof_files/', blank=True, null=True)  # New field
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    PAYMENT_TYPE_CHOICES = [
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
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    adults = models.IntegerField()
    children = models.IntegerField(default=0)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    
    
    def __str__(self):
        return f"Booking for {self.guest.name} - Room {self.room.room_no}"


class TeamMember(models.Model):
    image = models.ImageField(upload_to='team_images/', blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    email1 = models.EmailField(unique=True)
    email2 = models.EmailField(blank=True, null=True)
    phone1 = models.CharField(max_length=15, unique=True)
    phone2 = models.CharField(max_length=15, blank=True, null=True)
    address1 = models.TextField()
    address2 = models.TextField(blank=True, null=True)  
    account_name = models.CharField(max_length=100, unique=True)
    account_number = models.CharField(max_length=20, unique=True)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    github = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    aadhar_no = models.CharField(max_length=12, null=True, blank=True)
    pan_no = models.CharField(max_length=10, blank=True, null=True)
    aadhar_file = models.FileField(upload_to='aadhar_files/', blank=True, null=True)
    pan_file = models.FileField(upload_to='pan_files/', blank=True, null=True)

    class Meta:
        unique_together = ('name', 'email1', 'phone1', 'account_name', 'account_number', 'aadhar_no', 'pan_no')

    def __str__(self):
        return self.name
    

class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)  # e.g., Breakfast, Lunch, Dinner
    status = models.CharField(max_length=20)  # e.g., Available, Not Available
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='food_images/')  # Ensure you have Pillow installed

    def __str__(self):
        return self.name
    

class CustomUser(AbstractUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES,
        default='admin'
    )

    # Add any additional fields you need

    class Meta:
        db_table = 'hotelapp_customuser'
        permissions = [
            ("can_view_dashboard", "Can view dashboard"),
            # Add any other custom permissions
        ]

    def __str__(self):
        return self.username
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_created_at = models.DateTimeField(blank=True, null=True)  # New field

    def __str__(self):
        return self.user.username
    

# Signal to create a Profile when a CustomUser is created
@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    
