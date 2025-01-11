from django import forms
from .models import Room, Guest, Booking,TeamMember, FoodItem, CustomUser, RoomImage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
import re
import os
from django.contrib.auth.forms import UserCreationForm
from django.forms import ClearableFileInput
from django.contrib.auth.models import User

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
    features = forms.MultipleChoiceField(
        choices=[
            ('wifi', 'Wi-Fi'),
            ('tv', 'TV'),
            ('minibar', 'Minibar'),
            ('refrigerator', 'Refrigerator'),
            ('bathtub', 'Bath Tub'),
            ('parking', 'Parking'),
            ('pool', 'Swimming Pool'),
            ('cleaning', 'Room Cleaning'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    images = MultipleFileField(required=False)

    class Meta:
        model = Room
        fields = ['room_number', 'block', 'room_type', 'bed_type', 'ac_type', 
                  'base_price', 'weekend_price', 'holiday_price', 'hourly_price', 
                  'max_occupancy', 'seating_capacity', 'features','images', 'description']

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


    # def clean_room_number(self):
    #     # Skip validation for room_number if addition_type is 'bulk'
    #     if self.addition_type == 'bulk':
    #         return None
    #     room_number = self.cleaned_data.get('room_number')
    #     if not room_number:
    #         raise forms.ValidationError("This field is required.")
    #     return room_number
    
    def clean(self):
        cleaned_data = super().clean()
        room_type = cleaned_data.get('room_type')
        bed_type = cleaned_data.get('bed_type')
        seating_capacity = cleaned_data.get('seating_capacity')
        
        if room_type == 'conference' and not seating_capacity:
            raise forms.ValidationError("Seating capacity is required for conference rooms.")
        elif room_type != 'conference' and not bed_type:
            raise forms.ValidationError("Bed type is required for non-conference rooms.")
        
        return cleaned_data

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
    
class RoomSelectionForm(forms.Form):
    ROOM_TYPES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('vip', 'VIP Room'),
        ('conference', 'Conference Room'),
    ]
    room_type = forms.MultipleChoiceField(choices=ROOM_TYPES, widget=forms.CheckboxSelectMultiple)


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
            allowed_extensions = ['.pdf', '.doc', '.docx']
            ext = os.path.splitext(proof_file.name)[1]
            if ext.lower() not in allowed_extensions:
                raise forms.ValidationError("Please upload a valid document file (PDF, DOC, or DOCX) for proof.")


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

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Name is required.")
        return name

    def clean_email1(self):
        email = self.cleaned_data.get('email1')
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_phone1(self):
        phone = self.cleaned_data.get('phone1')
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number.")
        return phone

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if not account_number.isdigit():
            raise ValidationError("Account number must be numeric.")
        return account_number
    
    def clean_designation(self):
        designation=self.cleaned_data.get('designation')
        if not designation:
            raise ValidationError("Designation is requred.")
        return designation
    
    def clean_aadhar_no(self):
        aadhar_no = self.cleaned_data.get('aadhar_no')
        if not aadhar_no:
            raise ValidationError("Aadhar number is required.")
        if not aadhar_no.isdigit() or len(aadhar_no) != 12:
            raise ValidationError("Aadhar number must be 12 digits.")
        return aadhar_no

    def clean_pan_no(self):
        pan_no = self.cleaned_data.get('pan_no')
        if not pan_no:
            raise ValidationError("PAN number is required.")
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_no):
            raise ValidationError("Invalid PAN number format. It should be in the format ABCDE1234F.")
        return pan_no

    def clean_aadhar_file(self):
        aadhar_file = self.cleaned_data.get('aadhar_file')
        if not aadhar_file:
            raise ValidationError("Aadhar file is required.")
        return self._validate_file(aadhar_file, "Aadhar")

    def clean_pan_file(self):
        pan_file = self.cleaned_data.get('pan_file')
        if not pan_file:
            raise ValidationError("PAN file is required.")
        return self._validate_file(pan_file, "PAN")

    def _validate_file(self, file, file_type):
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if ext not in allowed_extensions:
                raise ValidationError(f"{file_type} file must be PDF, JPG, JPEG, or PNG.")
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError(f"{file_type} file size must be under 5MB.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email1')
        phone = cleaned_data.get('phone1')
        account_name = cleaned_data.get('account_name')
        account_number = cleaned_data.get('account_number')
        aadhar_no = cleaned_data.get('aadhar_no')
        pan_no = cleaned_data.get('pan_no')

        # Check for existing records, excluding the current instance
        existing_query = TeamMember.objects.filter(
            name=name, 
            email1=email, 
            phone1=phone, 
            account_name=account_name, 
            account_number=account_number, 
            aadhar_no=aadhar_no, 
            pan_no=pan_no
        )
        
        if self.instance:
            existing_query = existing_query.exclude(id=self.instance.id)
        
        # Check for unique Aadhar number
        if aadhar_no and TeamMember.objects.filter(aadhar_no=aadhar_no).exclude(id=self.instance.id).exists():
            raise ValidationError("Aadhar number must be unique.")

        # Check for unique PAN number
        if pan_no and TeamMember.objects.filter(pan_no=pan_no).exclude(id=self.instance.id).exists():
            raise ValidationError("PAN number must be unique.")

        return cleaned_data

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'price', 'category', 'status', 'description', 'image']

class VendorStaffRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

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
