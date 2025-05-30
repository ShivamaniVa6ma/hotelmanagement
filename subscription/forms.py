from django import forms
from django.core.validators import RegexValidator
from .models import SubscriptionPlan, SubscriptionDiscount, PlanFeature, SubscriptionUserDetails, ContactMessage, Tax
from django.forms import inlineformset_factory
from hotelapp.models import Guest
import re

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'description', 'monthly_price', 'is_popular', 'is_active', 'is_free_trial','is_logo_change','max_bookings_per_month','max_rooms','max_team_members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'monthly_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_popular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_free_trial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_logo_change': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_bookings_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_team_members': forms.NumberInput(attrs={'class': 'form-control'}),
        }
            

class PlanFeatureForm(forms.ModelForm):
    class Meta:
        model = PlanFeature
        fields = ['feature_text']
        widgets = {
            'feature_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter feature'
            })
        }

# Create a formset for features
PlanFeatureFormSet = inlineformset_factory(
    SubscriptionPlan,
    PlanFeature,
    form=PlanFeatureForm,
    extra=1,
    can_delete=True
)

class SubscriptionDiscountForm(forms.ModelForm):
    class Meta:
        model = SubscriptionDiscount
        fields = ['duration_months', 'discount_percentage']
        widgets = {
            'duration_months': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select duration'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01'
            })
        }


class GuestUpdateForm(forms.ModelForm):
    proof_file = forms.FileField(required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Guest
        fields = ['name', 'phone', 'email', 'address', 'proof_type', 'proof_no', 'proof_file', 'profile_picture']

    def clean(self):
        cleaned_data = super().clean()
        proof_type = cleaned_data.get('proof_type')
        proof_no = cleaned_data.get('proof_no')

        if proof_type and proof_no:
            if proof_type == 'aadhar' and (not proof_no.isdigit() or len(proof_no) != 12):
                raise forms.ValidationError("Aadhar number must be 12 digits")
            elif proof_type == 'pan' and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', proof_no):
                raise forms.ValidationError("Invalid PAN number format")
            elif proof_type == 'passport' and not re.match(r'^[A-Z]{1}[0-9]{7}$', proof_no):
                raise forms.ValidationError("Invalid passport number format")

        return cleaned_data

# class UserDetailsForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     email = forms.EmailField()
#     phone = forms.CharField(max_length=15)
#     company_name = forms.CharField(max_length=100)
#     number_of_rooms = forms.IntegerField(min_value=1)
#     address = forms.CharField(widget=forms.Textarea)

# class SubscriptionPlanForm(forms.ModelForm):
#     class Meta:
#         model = SubscriptionPlan
#         fields = ['name', 'description', 'monthly_price', 'is_popular', 'is_active','is_free_trial','is_logo_change','max_bookings_per_month','max_rooms','max_team_members']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'monthly_price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_popular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'is_free_trial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'is_logo_change': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

#             'max_bookings_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
#             'max_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
#             'max_team_members': forms.NumberInput(attrs={'class': 'form-control'}),

#         }

# class PlanFeatureForm(forms.ModelForm):
#     class Meta:
#         model = PlanFeature
#         fields = ['feature_text']
#         widgets = {
#             'feature_text': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter feature'
#             })
#         }

# # Create a formset for features
# # PlanFeatureFormSet = inlineformset_factory(
# #     SubscriptionPlan,
# #     PlanFeature,
# #     form=PlanFeatureForm,
# #     extra=1,
# #     can_delete=True,
# #     can_delete_extra=True,
# #     min_num=0,
# #     validate_min=True
# # )


# PlanFeatureFormSet = inlineformset_factory(
#     SubscriptionPlan,
#     PlanFeature,
#     form=PlanFeatureForm,
#     extra=1,
#     can_delete=True,
#     fields=['feature_text', 'id']
# )



# class SubscriptionDiscountForm(forms.ModelForm):
#     class Meta:
#         model = SubscriptionDiscount
#         fields = ['duration_months', 'discount_percentage']
#         widgets = {
#             'duration_months': forms.Select(
#                 choices=SubscriptionDiscount.DURATION_CHOICES,
#                 attrs={
#                     'class': 'form-select',
#                     'placeholder': 'Select duration'
#                 }
#             ),
#             'discount_percentage': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': '0',
#                 'max': '100',
#                 'step': '0.01'
#             })
#         }

# # Create a formset for discounts
# # DiscountFormSet = inlineformset_factory(
# #     SubscriptionPlan,
# #     SubscriptionDiscount,
# #     form=SubscriptionDiscountForm,
# #     extra=1,
# #     can_delete=True,
# #     can_delete_extra=True,
# #     min_num=0,
# #     validate_min=True
# # )

# DiscountFormSet = inlineformset_factory(
#     SubscriptionPlan,
#     SubscriptionDiscount,
#     form=SubscriptionDiscountForm,
#     extra=1,
#     can_delete=True,
#     fields=['duration_months', 'discount_percentage', 'id']
# )

class SubscriptionUserForm(forms.ModelForm):
    # Custom validators
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Override fields with custom validation
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'id': 'name'
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s]*$',
                message='Name can only contain letters and spaces'
            )
        ],
        error_messages={
            'required': 'Please enter your full name',
            'max_length': 'Name cannot be longer than 100 characters'
        }
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'email'
        }),
        error_messages={
            'required': 'Please enter your email address',
            'invalid': 'Please enter a valid email address'
        }
    )

    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'id': 'phone'
        }),
        validators=[phone_regex],
        error_messages={
            'required': 'Please enter your phone number',
            'max_length': 'Phone number cannot be longer than 15 digits'
        }
    )

    company_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter hotel/company name',
            'id': 'hotelName'
        }),
        error_messages={
            'required': 'Please enter your company name',
            'max_length': 'Company name cannot be longer than 100 characters'
        }
    )

    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your address',
            'id': 'address',
            'rows': '3'
        }),
        error_messages={
            'required': 'Please enter your address'
        }
    )

    class Meta:
        model = SubscriptionUserDetails
        fields = ['name', 'email', 'phone', 'company_name', 'address']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check minimum length
            if len(name.strip()) < 3:
                raise forms.ValidationError('Name must be at least 3 characters long')
            # Check if name contains numbers
            if any(char.isdigit() for char in name):
                raise forms.ValidationError('Name cannot contain numbers')
        return name.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if SubscriptionUserDetails.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already registered')
            # Additional email validation if needed
            if not email.strip():
                raise forms.ValidationError('Email cannot be empty')
        return email.lower().strip()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces or special characters
            phone = ''.join(filter(str.isdigit, phone))
            # Check minimum length
            if len(phone) < 10:
                raise forms.ValidationError('Phone number must be at least 10 digits')
        return phone

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name:
            # Check minimum length
            if len(company_name.strip()) < 2:
                raise forms.ValidationError('Company name must be at least 2 characters long')
            # Check for special characters
            if not all(char.isalnum() or char.isspace() for char in company_name):
                raise forms.ValidationError('Company name can only contain letters, numbers, and spaces')
        return company_name.strip()

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            # Check minimum length
            if len(address.strip()) < 10:
                raise forms.ValidationError('Address must be at least 10 characters long')
            # Check maximum length
            if len(address) > 500:
                raise forms.ValidationError('Address cannot be longer than 500 characters')
        return address.strip()

    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validations here if needed
        return cleaned_data

class UpgradeSubscriptionForm(forms.Form):
    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '12 Months'),
        (24, '24 Months'),
        (48, '48 Months'),
    ]
    
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.none(),  # Empty queryset by default
        empty_label=None,
        widget=forms.RadioSelect,
        label='Select Plan'
    )
    duration_months = forms.ChoiceField(
        choices=DURATION_CHOICES,
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Subscription Duration'
    )

    def __init__(self, *args, **kwargs):
        current_plan = kwargs.pop('current_plan', None)
        available_plans = kwargs.pop('available_plans', None)
        super().__init__(*args, **kwargs)
        
        if available_plans is not None:
            # Use the provided available plans
            self.fields['plan'].queryset = available_plans
        elif current_plan:
            # Fallback to filtering based on current plan
            self.fields['plan'].queryset = SubscriptionPlan.objects.filter(
                is_active=True
            ).exclude(
                is_free_trial=True
            )

    def clean(self):
        cleaned_data = super().clean()
        plan = cleaned_data.get('plan')
        
        if not plan:
            raise forms.ValidationError("Please select a plan")
            
        return cleaned_data
    

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']




class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'percentage','is_platform_fee']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Tax Name'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter Percentage'}),
            'is_platform_fee': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),  # RADIO FIELD

        }