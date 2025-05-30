from django import forms
from .models import Room, Guest,Tax, Booking,TeamMember, FoodItem, CustomUser, RoomImage, RoomType, LogoSettings, TeamDesignation, Event,Feature, Facility, ContactMessage,AboutUs
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
import re
import os
from django.contrib.auth.forms import UserCreationForm
from django.forms import ClearableFileInput
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from PIL import Image
from io import BytesIO


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
class RoomForm(forms.ModelForm):
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        empty_label="Select Room Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    images = MultipleFileField(required=False)

    class Meta:
        model = Room
        fields = ['room_number', 'block', 'room_type', 'bed_type', 'ac_type', 
                  'base_price', 'weekend_price', 'holiday_price', 'hourly_price', 
                  'max_occupancy', 'seating_capacity', 'features', 'images', 'description']
        
        widgets = {
            'room_type': forms.Select(attrs={'class': 'form-control', 'id': 'room_type'}),
            'bed_type': forms.Select(attrs={'class': 'form-control', 'id': 'bed_type'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'id': 'seating_capacity'}),
        }

    def save(self, commit=True):
        room = super().save(commit=commit)
        
        if commit:
            images = self.cleaned_data.get('images')
            if images:
                for image in images:
                    RoomImage.objects.create(room=room, image=image)
        
        return room

    def __init__(self, *args, **kwargs):
        # Pass addition_type context if available
        addition_type = kwargs.pop('addition_type', None)
        super().__init__(*args, **kwargs)

        if addition_type == 'bulk':
            self.fields.pop('room_number', None)

    def clean(self):
        cleaned_data = super().clean()
        room_type = cleaned_data.get("room_type")
        bed_type = cleaned_data.get("bed_type")

        if room_type and room_type.bed_type == "conference":
            # ✅ Allow conference rooms without a bed_type
            cleaned_data["bed_type"] = None
        elif not bed_type:
            raise forms.ValidationError("Bed type is required for non-conference rooms.")

        return cleaned_data

    # def clean_room_number(self):
    #     # Skip validation for room_number if addition_type is 'bulk'
    #     if self.addition_type == 'bulk':
    #         return None
    #     room_number = self.cleaned_data.get('room_number')
    #     if not room_number:
    #         raise forms.ValidationError("This field is required.")
    #     return room_number
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     room_type = cleaned_data.get('room_type')
    #     bed_type = cleaned_data.get('bed_type')
    #     seating_capacity = cleaned_data.get('seating_capacity')
        
    #     if room_type == 'conference' and not seating_capacity:
    #         raise forms.ValidationError("Seating capacity is required for conference rooms.")
    #     elif room_type != 'conference' and not bed_type:
    #         raise forms.ValidationError("Bed type is required for non-conference rooms.")
        
    #     return cleaned_data

class BulkRoomForm(forms.Form):
    from_room_number = forms.CharField(max_length=10)
    to_room_number = forms.CharField(max_length=10)
    
    def clean(self):
        cleaned_data = super().clean()
        from_room = cleaned_data.get('from_room_number')
        to_room = cleaned_data.get('to_room_number')
        
        if from_room and to_room:
            if from_room >= to_room:
                raise forms.ValidationError("'To Room Number' must be greater than 'From Room Number'")
        
        return cleaned_data
    
# class RoomSelectionForm(forms.Form):
#     ROOM_TYPES = [
#         ('standard', 'Standard Room'),
#         ('deluxe', 'Deluxe Room'),
#         ('vip', 'VIP Room'),
#         ('conference', 'Conference Room'),
#     ]
#     room_type = forms.MultipleChoiceField(choices=ROOM_TYPES, widget=forms.CheckboxSelectMultiple)

class GuestOTPForm(forms.Form):
    otp = forms.CharField(max_length=4)

class GuestForm(forms.ModelForm):
    PROOF_CHOICES = [
        ('aadhar', 'Aadhar Card'),
        ('pan', 'PAN Card'),
        ('passport', 'Passport'),
    ]
    
    proof_type = forms.ChoiceField(choices=PROOF_CHOICES, required=True)
    proof_no = forms.CharField(max_length=50, required=True)
    proof_file = forms.FileField(required=True)

    class Meta:
        model = Guest
        fields = ['name', 'phone', 'email', 'address', 'proof_type', 'proof_no', 'proof_file']

    def clean(self):
        cleaned_data = super().clean()
        proof_type = cleaned_data.get('proof_type')
        proof_no = cleaned_data.get('proof_no')
        proof_file=cleaned_data.get('proof_file')

        if proof_file:
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png','.webp','.doc', '.docx']
            ext = os.path.splitext(proof_file.name)[1]
            if ext.lower() not in allowed_extensions:
                raise forms.ValidationError("Please upload a valid document file (PDF, DOC, DOCX, JPG, JPEG, PNG, WEBP) for proof.")


        if not proof_type:
            print("Proof type is empty in clean method")  # Debug print
            raise forms.ValidationError("Please select an ID proof type")

        # Validate based on proof type
        if proof_type == 'aadhar':
            if not proof_no.isdigit() or len(proof_no) != 12:
                raise forms.ValidationError("Aadhar number must be 12 digits")
        elif proof_type == 'pan':
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', proof_no):
                raise forms.ValidationError("Invalid PAN number format")
        elif proof_type == 'passport':
            if not re.match(r'^[A-Z]{1}[0-9]{7}$', proof_no):
                raise forms.ValidationError("Invalid passport number format")

        return cleaned_data
    
    
class BookingForm(forms.ModelForm):
    check_in = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
    )
    check_out = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
    )

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'adults', 'children', 'payment_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'payment_type' in self.fields:
            # Make the field optional
            self.fields['payment_type'].required = False

            # Hide the field from the form
            self.fields['payment_type'].widget = forms.HiddenInput()

            # Set initial value
            self.fields['payment_type'].initial = 'razorpay'



    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        room = cleaned_data.get('room')

        if check_in and check_out and room:
            # Check if check-in is not in the past
            if check_in < timezone.now():
                raise ValidationError("Check-in time cannot be in the past")
            
            # Check if check-out is after check-in
            if check_out <= check_in:
                raise ValidationError("Check-out time must be after check-in time")

            # Check if room is available
            if not room.is_available:
                raise ValidationError("This room is not available for booking")

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=room
            ).filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
            )

            if overlapping_bookings.exists():
                raise ValidationError(
                    f"Room {room.room_no} is already booked for the selected dates. "
                    "Please choose different dates or another room."
                )

        return cleaned_data

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            'image', 'name', 'description', 'email1', 'email2', 'phone1', 'phone2',
            'address1', 'address2', 'account_name', 'account_number',
            'ifsc_code', 'bank_name', 'facebook', 'twitter',
            'linkedin', 'github', 'designation', 'aadhar_no', 'pan_no', 'aadhar_file', 'pan_file'
        ]

    def __init__(self, *args, **kwargs):
        """ Accept `subscription_user` as an additional argument """
        self.subscription_user = kwargs.pop('subscription_user', None)
        super(TeamMemberForm, self).__init__(*args, **kwargs)

    def clean_email1(self):
        email = self.cleaned_data.get('email1')
        if not email:
            raise forms.ValidationError("Email is required.")
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        
        # Check uniqueness within the same subscription user
        if self.subscription_user and TeamMember.objects.filter(subscription_user=self.subscription_user, email1=email).exists():
            raise forms.ValidationError("A team member with this email already exists.")
        
        return email.lower()

    def clean_phone1(self):
        phone = self.cleaned_data.get('phone1')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise forms.ValidationError("Enter a valid phone number in the format +999999999. Up to 15 digits allowed.")
        
        # Check uniqueness within the same subscription user
        if self.subscription_user and TeamMember.objects.filter(subscription_user=self.subscription_user, phone1=phone).exists():
            raise forms.ValidationError("A team member with this phone number already exists.")
        
        return phone

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if not account_number:
            raise forms.ValidationError("Account number is required.")
        if not account_number.isdigit():
            raise forms.ValidationError("Account number must be numeric.")
        if not 9 <= len(account_number) <= 18:
            raise forms.ValidationError("Account number must be between 9 and 18 digits.")

        # Check uniqueness within the same subscription user
        if self.subscription_user and TeamMember.objects.filter(subscription_user=self.subscription_user, account_number=account_number).exists():
            raise forms.ValidationError("A team member with this account number already exists.")

        return account_number

    def clean_aadhar_no(self):
        aadhar_no = self.cleaned_data.get('aadhar_no')
        if not aadhar_no:
            raise forms.ValidationError("Aadhar number is required.")
        if not aadhar_no.isdigit() or len(aadhar_no) != 12:
            raise forms.ValidationError("Aadhar number must be exactly 12 digits.")
        
        # Check uniqueness within the same subscription user
        if self.subscription_user and TeamMember.objects.filter(subscription_user=self.subscription_user, aadhar_no=aadhar_no).exists():
            raise forms.ValidationError("A team member with this Aadhar number already exists.")

        return aadhar_no

    def clean_pan_no(self):
        pan_no = self.cleaned_data.get('pan_no')
        if not pan_no:
            raise forms.ValidationError("PAN number is required.")
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_no):
            raise forms.ValidationError("Invalid PAN number format. It should be in the format ABCDE1234F.")

        # Check uniqueness within the same subscription user
        if self.subscription_user and TeamMember.objects.filter(subscription_user=self.subscription_user, pan_no=pan_no).exists():
            raise forms.ValidationError("A team member with this PAN number already exists.")

        return pan_no

    def clean(self):
        """ Final validation to ensure all checks pass """
        cleaned_data = super().clean()
        return cleaned_data

        

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'price', 'category', 'status', 'description', 'image']

# class VendorStaffRegistrationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'password1', 'password2', 'user_type']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)

class ResetPasswordForm(forms.Form):
    password = forms.CharField(label="New Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'available_from','bed_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your room type'}),
            'available_from': forms.DateInput(attrs={'type': 'datetime-local'}),
            'bed_type': forms.RadioSelect,  # Use RadioSelect for bed type

        }

    def __init__(self, *args, **kwargs):
        super(RoomTypeForm, self).__init__(*args, **kwargs)
        # Set the initial value of available_from to the current date and time
        self.fields['available_from'].initial = datetime.now()

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.strip():
            raise ValidationError("Room type name cannot be empty.")
        if any(char in "!@#$%^&*()<>?/|}{~:" for char in name):
            raise ValidationError("Room type name cannot contain special characters.")
        return name

    # def clean_available_from(self):
    #     available_from = self.cleaned_data.get('available_from')
    #     if available_from and available_from < timezone.now():  # ✅ Correct
    #         raise forms.ValidationError("Available from date cannot be in the past.")
    #     return available_from

class LogoSettingsForm(forms.ModelForm):
    class Meta:
        model = LogoSettings
        fields = ['site_name', 'favicon', 'light_logo', 'dark_logo']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your hotel name'}),
            'favicon': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'light_logo': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
            'dark_logo': forms.ClearableFileInput(attrs={'class': 'form-control file-input'}),
        }

    def clean_site_name(self):
        site_name = self.cleaned_data.get('site_name')
        if not site_name.strip():
            raise ValidationError("Site name cannot be empty.")
        return site_name

    def clean_favicon(self):
        return self.validate_image_file(self.cleaned_data.get('favicon'), "favicon")

    def clean_light_logo(self):
        return self.validate_image_file(self.cleaned_data.get('light_logo'), "light logo")

    def clean_dark_logo(self):
        return self.validate_image_file(self.cleaned_data.get('dark_logo'), "dark logo")

    def validate_image_file(self, file, field_name):
        """Reusable function to validate image file type and size"""
        if file:
            if not file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.ico')):
                raise ValidationError(f"Invalid file format for {field_name}. Allowed formats: PNG, JPG, JPEG, ICO.")
            if file.size > 2 * 1024 * 1024:  # Limit to 2MB
                raise ValidationError(f"{field_name.capitalize()} size should not exceed 2MB.")
        return file


class TeamDesignationForm(forms.ModelForm):
    class Meta:
        model = TeamDesignation
        fields = ['designation', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'readonly': 'readonly'}),
        }
        labels = {
            'designation': 'Team Designation',
            'date_time': 'Date and Time',
        }
        
    def __init__(self, *args, **kwargs):
        super(TeamDesignationForm, self).__init__(*args, **kwargs)
        # Set the initial value of date_time to the current date and time
        self.fields['date_time'].initial = datetime.now()

    def clean_designation(self):
        designation = self.cleaned_data.get('designation')
        if not designation.strip():
            raise forms.ValidationError("Designation cannot be empty.")
        if any(char.isdigit() for char in designation):
            raise forms.ValidationError("Designation cannot contain numbers.")
        if any(char in "!@#$%^&*()<>?/|}{~:" for char in designation):
            raise forms.ValidationError("Designation cannot contain special characters.")
        return designation

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time and date_time < datetime.now():
            raise forms.ValidationError("Date and time cannot be in the past.")
        return date_time

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['occasion', 'start_date', 'end_date']
        widgets = {
            'occasion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter occasion'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be before end date.")

class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Swimming Pool'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the feature...'}),
        }

class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = ['name', 'description', 'image', 'icon']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['image'].required = False
        self.fields['icon'].required = False

    def validate_file_field(self, field_name, display_name):
        file = self.cleaned_data.get(field_name)

        if file:
            # ✅ Extension check
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f"{display_name.capitalize()} must be a valid image file (JPG, PNG, GIF, WEBP)."
                )

            # ✅ Content-Type check
            valid_mime_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp'
            ]
            if hasattr(file, 'content_type') and file.content_type not in valid_mime_types:
                raise forms.ValidationError(
                    f"{display_name.capitalize()} format not supported. Please upload a valid image."
                )

            # ✅ File size check
            max_size = 2 * 1024 * 1024  # 2MB
            if file.size > max_size:
                raise forms.ValidationError(
                    f"{display_name.capitalize()} size must be under 2MB."
                )

        return file

    def clean_image(self):
        return self.validate_file_field('image', 'Image')

    def clean_icon(self):
        return self.validate_file_field('icon', 'Icon')



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long")
        if not re.match("^[a-zA-Z\s]*$", name):
            raise forms.ValidationError("Name should only contain letters and spaces")
        return name

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 5:
            raise forms.ValidationError("Subject must be at least 5 characters long")
        return subject

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long")
        return message

class AboutUsForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        fields = ['image', 'title', 'description']
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) > 100:
            raise forms.ValidationError("Title cannot exceed 100 characters.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) > 500:
            raise forms.ValidationError("Description cannot exceed 500 characters.")
        return description
    
    def validate_file_field(self, field_name, display_name):
        file = self.cleaned_data.get(field_name)

        if file:
            # ✅ Extension check
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f"{display_name.capitalize()} must be a valid image file (JPG, PNG, GIF, WEBP)."
                )

            # ✅ Content-Type check
            valid_mime_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp'
            ]
            if hasattr(file, 'content_type') and file.content_type not in valid_mime_types:
                raise forms.ValidationError(
                    f"{display_name.capitalize()} format not supported. Please upload a valid image."
                )

            # ✅ File size check
            max_size = 2 * 1024 * 1024  # 2MB
            if file.size > max_size:
                raise forms.ValidationError(
                    f"{display_name.capitalize()} size must be under 2MB."
                )

        return file

class AvailabilityForm(forms.Form):
    check_in = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
    )
    check_out = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
    )
    room_type = forms.CharField(required=False)

class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Tax Name'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter Percentage'}),
        }