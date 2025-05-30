import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Payment, SubscriptionPlan, SubscriptionUserDetails, SubscriptionDiscount, PlanFeature, Cart,ContactMessage,Tax
import json
from django.contrib import messages
from .forms import SubscriptionPlanForm, SubscriptionDiscountForm,TaxForm, PlanFeatureFormSet,PlanFeatureForm, SubscriptionUserForm, UpgradeSubscriptionForm,ContactForm,GuestUpdateForm
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
import uuid
from django.http import HttpResponse

import requests
from requests.exceptions import RequestException
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.http import urlencode
from urllib.parse import quote
from django.utils.decorators import method_decorator
from decimal import Decimal
from django.db import transaction
from django.forms import modelformset_factory
from hotelapp.models import LogoSettings,Guest,CustomUser,Booking,Room
import random
from django.contrib.auth import get_user_model
from hotelapp.decorators import superuser_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from calendar import month_name
from django.utils.timezone import now
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views.decorators.http import require_POST

# Initialize Razorpay client with timeout
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
    requests_kwargs={
        'timeout': 30,  # Set timeout to 30 seconds
        'verify': True  # Verify SSL certificates
    }
)

# Helper function to check if user is superuser
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

CustomUser = get_user_model()

# Create the DiscountFormSet using inlineformset_factory
DiscountFormSet = inlineformset_factory(
    SubscriptionPlan,  # parent model
    SubscriptionDiscount,  # child model
    form=SubscriptionDiscountForm,
    extra=1,  # number of empty forms to display
    can_delete=True  # allow deleting existing discounts
)

# def create_payment(request):
#     plan_id = request.GET.get('plan')
#     try:
#         plan = SubscriptionPlan.objects.get(id=plan_id)
#         amount = int(float(plan.yearly_price if request.GET.get('yearly') else plan.monthly_price) * 100)
        
#         # Updated payment data with more options
#         payment_data = {
#             'amount': amount,
#             'currency': 'INR',
#             'receipt': f'order_rcptid_{plan_id}',
#             'payment_capture': 1,  # Auto-capture payment
#             'notes': {
#                 'plan_id': plan_id,
#                 'user_email': request.user.email if request.user.is_authenticated else ''
#             }
#         }
        
#         order = client.order.create(data=payment_data)
        
#         payment = Payment.objects.create(
#             user=request.user if request.user.is_authenticated else None,
#             order_id=order['id'],
#             amount=amount/100,
#             currency='INR'
#         )
        
#         context = {
#             'order_id': order['id'],
#             'amount': amount,
#             'currency': 'INR',
#             'razorpay_key': settings.RAZORPAY_KEY_ID,
#             'plan': plan,
#             'callback_url': request.build_absolute_uri('/subscription/payment-callback/'),
#             # Add user details for prefill
#             'user_name': request.user.get_full_name() if request.user.is_authenticated else '',
#             'user_email': request.user.email if request.user.is_authenticated else '',
#             'user_contact': request.user.phone if hasattr(request.user, 'phone') else ''
#         }
        
#         return render(request, 'subscription/cart_page.html', context)
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)

def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).prefetch_related('plan_features', 'discounts')

    # Prepare a list to hold plan details with discounts
    plan_details = []
    for plan in plans:
        duration_months = 1  # Default duration for discount calculation
        discounted_price = plan.get_discounted_price(duration_months)
        discount_percentage = plan.discounts.filter(duration_months=duration_months).first()
        discount_percentage = discount_percentage.discount_percentage if discount_percentage else 0

        plan_details.append({
            'plan': plan,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'is_popular': plan.is_popular,
        })

    return render(request, 'subscription/pricing.html', {
        'plan_details': plan_details
    })

def cart_page(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Define all possible subscription months
    all_durations = [1, 3, 6, 12, 24, 48]
    
    # Get available discounts for the plan
    discounts = {}
    
    # Initialize all durations with 0 discount
    for duration in all_durations:
        discounts[str(duration)] = {
            'percentage': 0,
            'monthly_price': float(plan.monthly_price)
        }
    
    # Update discounts where available
    for discount in plan.discounts.all():
        discounts[str(discount.duration_months)] = {
            'percentage': float(discount.discount_percentage),
            'monthly_price': float(plan.get_discounted_price(discount.duration_months))
        }
    
    # Create duration choices for all months
    duration_choices = [(months, f"{months} Months" if months > 1 else "1 Month") 
                       for months in all_durations]
    
    if request.method == 'POST':
        duration_months = int(request.POST.get('duration_months', 1))

        request.session['selected_plan'] = {
            'plan_id': plan_id,
            'monthly_price': discounts[str(duration_months)]['monthly_price'],
            'duration_months': duration_months,
        }
        return redirect('subscription:user_details', plan_id=plan_id, duration=duration_months)
    
    context = {
        'plan': plan,
        'discounts': json.dumps(discounts),
        'duration_choices': duration_choices
    }
    
    return render(request, 'subscription/cart_page.html', context)

def user_details(request, plan_id, duration):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        form = SubscriptionUserForm(request.POST)
        if form.is_valid():
            try:
                user_details = form.save(commit=False)
                user_details.booking_id = f"BOOK_{uuid.uuid4().hex[:8].upper()}"
                user_details.subscription_plan = plan  # Set the subscription plan
                
                # Generate a secret key if not already set
                if not user_details.secret_key:
                    user_details.secret_key = uuid.uuid4().hex  # Generate a new secret key
                
                user_details.save()
                
                # Clear any previous session data related to subscriptions
                request.session.flush()  # Clear all session data
                
                # Create cart with duration
                cart = Cart.objects.create(
                    user_details=user_details,
                    plan=plan,
                    duration_months=duration
                )
                
                request.session['cart_id'] = cart.id
                request.session.modified = True
                
                # Check if the plan is a free trial
                if plan.is_free_trial:
                    # Send free trial email
                    send_free_trial_email(user_details)
                # else:
                #     # Send regular subscription email
                #     send_subscription_email(cart)

                return redirect('subscription:create_payment')
                
            except Exception as e:
                print(f"Error saving form: {str(e)}")  # Debug print
                form.add_error(None, str(e))
        else:
            # Handle form errors
            error_messages = []
            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                messages.error(request, '<br>'.join(error_messages))
    else:
        form = SubscriptionUserForm()
    
    context = {
        'form': form,
        'plan': plan,
        'duration': duration,
        'form_errors': form.errors if request.method == 'POST' else None
    }
    
    return render(request, 'subscription/user_form.html', context)

# def create_payment(request):
#     cart_id = request.session.get('cart_id')
#     if not cart_id:
#         return JsonResponse({'error': 'Cart not found'}, status=400)
    
#     try:
#         cart = Cart.objects.get(id=cart_id)
        
#         # Check if the user is subscribing for the first time
#         is_first_time_subscriber = cart.user_details.subscription_end_date is None
        
#         if cart.plan.is_free_trial:
#             # Handle free trial
#             user_details = cart.user_details
#             user_details.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
#             user_details.is_active = True
#             user_details.save()
#             messages.success(request, 'You have successfully signed up for a free trial! You have access for 1 month.')
#             return redirect('subscription:payment_success')  # Redirect to success page for first-time users
        
#         # Get credit amount from session
#         credit_amount = float(request.session.get('credit_amount', 0))
#         original_price = float(request.session.get('original_price', cart.get_total()))
        
#         # Calculate final amount after credit
#         final_amount = max(0, original_price - credit_amount)
#         amount_in_paisa = int(final_amount * 100)  # Convert to paisa
        
#         # Handle zero-cost upgrade
#         if amount_in_paisa == 0:
#             try:
#                 # Create payment record for tracking
#                 payment = Payment.objects.create(
#                     user_details=cart.user_details,
#                     cart=cart,
#                     amount=0,
#                     payment_id=f'zero_cost_upgrade_{uuid.uuid4().hex}',
#                     order_id=f'free_upgrade_{uuid.uuid4().hex}',
#                     status='completed'
#                 )
                
#                 # Update subscription details
#                 user_details = cart.user_details
#                 is_same_plan = request.session.get('is_same_plan', False)
                
#                 if is_same_plan:
#                     new_end_date = user_details.subscription_end_date + timezone.timedelta(days=cart.duration_months * 30)
#                 else:
#                     new_end_date = timezone.now() + timezone.timedelta(days=cart.duration_months * 30)
                
#                 user_details.subscription_plan = cart.plan
#                 user_details.subscription_end_date = new_end_date
#                 user_details.save()
                
#                 # Send subscription confirmation email
#                 send_subscription_email(payment)
                
#                 # Clear session data
#                 request.session.pop('cart_id', None)
#                 request.session.pop('credit_amount', None)
#                 request.session.pop('original_price', None)
#                 request.session.pop('is_same_plan', None)
                
#                 messages.success(request, f'Your subscription has been successfully upgraded to {cart.plan.name} plan!')
#                 return redirect('subscription:subscription_status')  # Redirect to subscription status for upgrades
                
#             except Exception as e:
#                 print(f"Zero-cost upgrade error: {str(e)}")
#                 messages.error(request, 'Error processing zero-cost upgrade. Please try again.')
#                 return redirect('subscription:subscription_status')
        
#         # Create Razorpay Order
#         payment_data = {
#             'amount': amount_in_paisa,
#             'currency': 'INR',
#             'receipt': f'order_{uuid.uuid4().hex}',
#             'payment_capture': 1,
#             'notes': {
#                 'original_price': str(original_price),
#                 'credit_amount': str(credit_amount),
#                 'final_amount': str(final_amount),
#                 'is_upgrade': 'false'  # Indicate this is a new subscription
#             }
#         }
        
#         order = client.order.create(data=payment_data)
        
#         # Create local payment record
#         payment = Payment.objects.create(
#             user_details=cart.user_details,
#             cart=cart,
#             amount=final_amount,
#             payment_id=order['id'],
#             order_id=payment_data['receipt']
#         )
        
#         # Redirect to payment page for new subscriptions
#         if is_first_time_subscriber:
#             return render(request, 'subscription/payment.html', {
#                 'payment': payment,
#                 'order_id': order['id'],
#                 'amount': amount_in_paisa,
#                 'currency': 'INR',
#                 'razorpay_key': settings.RAZORPAY_KEY_ID,
#                 'callback_url': request.build_absolute_uri('/subscription/payment-callback/'),
#                 'original_price': original_price,
#                 'credit_amount': credit_amount,
#                 'final_amount': final_amount
#             })
#         else:
#             return redirect('subscription:subscription_status')  # For upgrades, show status
            
#     except Exception as e:
#         print(f"Payment creation error: {str(e)}")
#         messages.error(request, str(e))
#         return redirect('subscription:subscription_status')

def create_payment(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        return JsonResponse({'error': 'Cart not found'}, status=400)
    
    try:
        cart = Cart.objects.get(id=cart_id)
        is_first_time_subscriber = cart.user_details.subscription_end_date is None

        if cart.plan.is_free_trial:
            user_details = cart.user_details
            user_details.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
            user_details.is_active = True
            user_details.save()
            messages.success(request, 'You have successfully signed up for a free trial! You have access for 1 month.')
            return redirect('subscription:payment_success')

        credit_amount = float(request.session.get('credit_amount', 0))
        base_price = float(request.session.get('original_price', cart.get_total()))

        # 🔽 Updated Tax Logic for multiple tax entries
        taxes = Tax.objects.filter(is_platform_fee=False)  # ✅ Only non-platform taxes
        tax_details = []
        total_tax_amount = 0
        total_tax_percentage = 0

        for tax in taxes:
            percentage = float(tax.percentage or 0)
            tax_amount = (base_price * percentage) / 100
            total_tax_amount += tax_amount
            total_tax_percentage += percentage
            tax_details.append({
                'name': tax.name,
                'percentage': percentage,
                'amount': tax_amount
            })

        total_price_with_tax = base_price + total_tax_amount
        final_amount = max(0, total_price_with_tax - credit_amount)
        amount_in_paisa = int(final_amount * 100)

        if amount_in_paisa == 0:
            try:
                payment = Payment.objects.create(
                    user_details=cart.user_details,
                    cart=cart,
                    amount=0,
                    payment_id=f'zero_cost_upgrade_{uuid.uuid4().hex}',
                    order_id=f'free_upgrade_{uuid.uuid4().hex}',
                    status='completed',
                    tax_amount=Decimal(total_tax_amount),
                    tax_percentage=Decimal(total_tax_percentage)
                )

                user_details = cart.user_details
                is_same_plan = request.session.get('is_same_plan', False)

                if is_same_plan:
                    new_end_date = user_details.subscription_end_date + timezone.timedelta(days=cart.duration_months * 30)
                else:
                    new_end_date = timezone.now() + timezone.timedelta(days=cart.duration_months * 30)

                user_details.subscription_plan = cart.plan
                user_details.subscription_end_date = new_end_date
                user_details.save()

                send_subscription_email(payment)

                # Clear session
                for key in ['cart_id', 'credit_amount', 'original_price', 'is_same_plan']:
                    request.session.pop(key, None)

                messages.success(request, f'Your subscription has been successfully upgraded to {cart.plan.name} plan!')
                return redirect('subscription:subscription_status')
            except Exception as e:
                print(f"Zero-cost upgrade error: {str(e)}")
                messages.error(request, 'Error processing zero-cost upgrade. Please try again.')
                return redirect('subscription:subscription_status')

        # Razorpay Order Creation
        payment_data = {
            'amount': amount_in_paisa,
            'currency': 'INR',
            'receipt': f'order_{uuid.uuid4().hex}',
            'payment_capture': 1,
            'notes': {
                'original_price': str(base_price),
                'tax_percentage': str(total_tax_percentage),
                'tax_amount': str(total_tax_amount),
                'credit_amount': str(credit_amount),
                'final_amount': str(final_amount),
                'is_upgrade': 'false'
            }
        }

        order = client.order.create(data=payment_data)

        payment = Payment.objects.create(
            user_details=cart.user_details,
            cart=cart,
            amount=final_amount,
            payment_id=order['id'],
            order_id=payment_data['receipt'],
            tax_amount=Decimal(total_tax_amount),
            tax_percentage=Decimal(total_tax_percentage)
        )

        return render(request, 'subscription/payment.html', {
            'payment': payment,
            'order_id': order['id'],
            'amount': amount_in_paisa,
            'currency': 'INR',
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'callback_url': request.build_absolute_uri('/subscription/payment-callback/'),
            'original_price': base_price,
            'credit_amount': credit_amount,
            'final_amount': final_amount,
            'tax_amount': total_tax_amount,
            'tax_percentage': total_tax_percentage,
            'tax_details': tax_details
        })

    except Exception as e:
        print(f"Payment creation error: {str(e)}")
        messages.error(request, str(e))
        return redirect('subscription:subscription_status')

def send_subscription_email(payment):
    try:
        user_details = payment.user_details
        cart = payment.cart
        
        # Construct signup URL with proper URL encoding
        signup_url = (
            f"{settings.SITE_URL}/admin-panel/signup/"  # Changed to admin-panel
            f"?email={quote(user_details.email)}"
            f"&secret_key={quote(user_details.secret_key)}"
        )
        # ✅ Use invoice_id, not payment.id
        invoice_url = f"{settings.SITE_URL}/subscription/invoice/{payment.invoice_id}/"

        print(f"Generated signup URL: {signup_url}")
        print(f"Generated invoice URL: {invoice_url}")

        context = {
            'name': user_details.name,
            'company_name': user_details.company_name,
            'plan_name': cart.plan.name,
            'duration_months': cart.duration_months,
            'amount': payment.amount,
            'booking_id': user_details.booking_id,
            'payment_id': payment.payment_id,
            'secret_key': user_details.secret_key,
            'signup_url': signup_url,
            'user_details': user_details,
            'site_url': settings.SITE_URL.rstrip('/'),
            'invoice_url': invoice_url,  # <-- Add this line
            'payment': payment  # <-- Add this line

        }
        
        # Render email templates
        html_message = render_to_string('subscription/subscription_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Subscription Confirmation - Hotel Management System',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_details.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def send_free_trial_email(user_details):
    try:
        print(f"Preparing to send free trial email to: {user_details.email}")  # Debug print
        
        # Check if subscription_plan is None
        if user_details.subscription_plan is None:
            print("Error: Subscription plan is None.")  # Debug print
            return False
        
        # Construct signup URL with proper URL encoding
        signup_url = (
            f"{settings.SITE_URL}/admin-panel/signup/"
            f"?email={quote(user_details.email)}"
            f"&secret_key={quote(user_details.secret_key)}"
        )
        
        print(f"Generated signup URL for free trial: {signup_url}")  # Debug print
        
        context = {
            'name': user_details.name,
            'company_name': user_details.company_name,
            'plan_name': user_details.subscription_plan.name,
            'subscription_end_date': user_details.subscription_end_date,
            'signup_url': signup_url,
            'user_details': user_details,
            'site_url': settings.SITE_URL.rstrip('/')
        }
        
        # Render email templates for free trial
        html_message = render_to_string('subscription/free_trial_email.html', context)
        plain_message = strip_tags(html_message)
        
        print("Sending email...")  # Debug print
        
        send_mail(
            subject='Welcome to Your Free Trial - Hotel Management System',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_details.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print("Email sent successfully!")  # Debug print
        return True
    except Exception as e:
        print(f"Free trial email sending failed: {str(e)}")
        return False
 
@csrf_exempt
def payment_callback(request):
    try:
        # Handle zero-cost upgrade confirmation
        if request.method == 'POST' and request.POST.get('zero_cost_upgrade'):
            cart_id = request.session.get('cart_id')
            if not cart_id:
                messages.error(request, 'Cart not found')
                return redirect('subscription:plans')
            
            try:
                cart = Cart.objects.get(id=cart_id)
                user_details = cart.user_details
                is_same_plan = request.session.get('is_same_plan', False)
                
                if is_same_plan:
                    new_end_date = user_details.subscription_end_date + timezone.timedelta(days=cart.duration_months * 30)
                else:
                    new_end_date = timezone.now() + timezone.timedelta(days=cart.duration_months * 30)
                
                # Update subscription details
                user_details.subscription_plan = cart.plan
                user_details.subscription_end_date = new_end_date
                user_details.save()
                
                # Create a payment record for tracking
                Payment.objects.create(
                    user_details=user_details,
                    cart=cart,
                    amount=0,
                    payment_id='zero_cost_upgrade',
                    order_id=f'free_upgrade_{uuid.uuid4().hex}',
                    status='completed'
                )
                
                # Clear session data
                request.session.pop('cart_id', None)
                request.session.pop('credit_amount', None)
                request.session.pop('original_price', None)
                request.session.pop('is_same_plan', None)
                
                messages.success(request, f'Your subscription has been successfully upgraded to {cart.plan.name} plan!')
                return redirect('subscription:payment_success')
                
            except Cart.DoesNotExist:
                messages.error(request, 'Invalid cart')
                return redirect('subscription:subscription_status')
        
        # Handle regular payment verification
        if request.method == 'POST':
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
        else:
            payment_id = request.GET.get('razorpay_payment_id', '')
            order_id = request.GET.get('razorpay_order_id', '')
            signature = request.GET.get('razorpay_signature', '')
        
        if not payment_id or not order_id or not signature:
            print(f"Missing payment details - payment_id: {payment_id}, order_id: {order_id}, signature: {signature}")
            messages.error(request, 'Payment verification failed. Missing payment details.')
            return redirect('subscription:subscription_status')
            
        # Get the payment record using payment_id field which contains the Razorpay order ID
        try:
            payment = Payment.objects.get(payment_id=order_id)
            print(f"Found payment record: {payment.id} for order_id: {order_id}")
            cart = payment.cart
        except Payment.DoesNotExist:
            print(f"Payment record not found for order_id: {order_id}")
            messages.error(request, 'Payment record not found')
            return redirect('subscription:subscription_status')
            
        # Verify payment signature
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature(params_dict)
            
            # Update payment status and payment_id
            payment.status = 'completed'
            payment.razorpay_payment_id = payment_id  # Store the actual payment ID in a new field
            payment.save()
            
            # Send confirmation email
            email_sent = send_subscription_email(payment)
            if not email_sent:
                print("Warning: Subscription confirmation email failed to send")
            
            # Update subscription
            user_details = cart.user_details
            is_same_plan = request.session.get('is_same_plan', False)
            
            if is_same_plan:
                new_end_date = user_details.subscription_end_date + timezone.timedelta(days=cart.duration_months * 30)
            else:
                new_end_date = timezone.now() + timezone.timedelta(days=cart.duration_months * 30)
            
            user_details.subscription_plan = cart.plan
            user_details.subscription_end_date = new_end_date
            user_details.save()
            
            # Clear session data
            request.session.pop('cart_id', None)
            request.session.pop('credit_amount', None)
            request.session.pop('original_price', None)
            request.session.pop('is_same_plan', None)
            
            messages.success(request, f'Your subscription has been successfully upgraded to {cart.plan.name} plan!')
            return redirect('subscription:payment_success')
            
        except Exception as e:
            print(f"Payment verification error: {str(e)}")
            messages.error(request, 'Payment verification failed')
            return redirect('subscription:payment_failed')
            
    except Exception as e:
        print(f"Payment callback error: {str(e)}")
        messages.error(request, str(e))
        return redirect('subscription:payment_failed')

def get_bank_details(razorpay_payment_id):
    try:
        razorpay_payment = client.payment.fetch(razorpay_payment_id)
        print("Razorpay Payment Response:", razorpay_payment)

        method = razorpay_payment.get('method')
        bank = razorpay_payment.get('bank')
        bank_txn_id = razorpay_payment.get('acquirer_data', {}).get('bank_transaction_id', '')

        if method == 'netbanking' and bank:
            return {
                'bank': bank,
                'txn_id': bank_txn_id,
            }

    except Exception as e:
        print("Error fetching Razorpay payment details:", e)

    return {
        'bank': 'Unavailable',
        'txn_id': bank_txn_id or 'Unavailable',
        # 'ifsc': 'Unavailable',
    }


def subscription_invoice(request, invoice_id):
    payment = get_object_or_404(Payment, invoice_id=invoice_id)

    if not payment.user_details:
        return HttpResponse("This payment does not have associated user details.", status=400)

    user_details = payment.user_details

    # Safely retrieve and convert credit amount to Decimal
    credit_amount = Decimal(str(request.session.get('credit_amount', 0)))
    tax_amount = payment.tax_amount if payment.tax_amount else Decimal('0.00')

    default_original_price = payment.amount - tax_amount + credit_amount
    bank_details = get_bank_details(payment.razorpay_payment_id) if payment.razorpay_payment_id else {}


    context = {
        'payment': payment,
        'user_details': user_details,
        'original_price': request.session.get('original_price', default_original_price),
        'credit_amount': credit_amount,
        'bank_details': bank_details,
    }
    return render(request, 'subscription/invoice.html', context)




# def render_invoice(request, payment_id):
#     payment = get_object_or_404(Payment, id=payment_id)
#     user_details = payment.subscription_user  # assuming FK to SubscriptionUserDetails
#     plan = payment.plan  # assuming FK to SubscriptionPlan

#     context = {
#         'payment': payment,
#         'user_details': user_details,
#         'plan': plan,
#     }
#     return render(request, 'subscription/invoice.html', context)

def payment_success(request):
    payment_id = request.session.pop('last_payment_id', None)
    if not payment_id:
        messages.error(request, "No recent payment found.")
        return redirect('subscription:plans')

    try:
        payment = Payment.objects.get(id=payment_id)
        return render(request, 'subscription/payment_success.html', {
            'payment_id': payment.razorpay_payment_id or payment.payment_id,
            'subscription_plan': payment.cart.plan.name,
            'amount': payment.amount
        })
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('subscription:plans')


def payment_failed(request):
    return render(request, 'subscription/payment_failed.html')

def payment_cancel(request):
    return render(request, 'subscription/payment_cancel.html')

@login_required
@superuser_required
def create_plan(request):
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        feature_formset = PlanFeatureFormSet(request.POST, prefix='features')
        discount_formset = DiscountFormSet(request.POST, prefix='discounts')

        if form.is_valid() and feature_formset.is_valid() and discount_formset.is_valid():
            plan = form.save()
            
            # Set instance and save features
            feature_formset.instance = plan
            feature_formset.save()

            # Set instance and save discounts
            discount_formset.instance = plan
            discount_formset.save()

            messages.success(request, 'Subscription plan created successfully!')
            return redirect('subscription:plans')
    else:
        form = SubscriptionPlanForm()
        feature_formset = PlanFeatureFormSet(prefix='features')
        discount_formset = DiscountFormSet(prefix='discounts')

    return render(request, 'super_admin/create_plan.html', {
        'form': form,
        'feature_formset': feature_formset,
        'discount_formset': discount_formset
    })

@transaction.atomic
def edit_plan(request, pk):
    plan = get_object_or_404(SubscriptionPlan, pk=pk)

    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        feature_formset = PlanFeatureFormSet(request.POST, instance=plan, prefix='features')
        discount_formset = DiscountFormSet(request.POST, instance=plan, prefix='discounts')

        if form.is_valid() and feature_formset.is_valid() and discount_formset.is_valid():
            with transaction.atomic():
                plan = form.save()
                
                # Save features and discounts automatically
                feature_formset.instance = plan
                feature_formset.save()

                discount_formset.instance = plan
                discount_formset.save()

                messages.success(request, 'Plan updated successfully!')
                return redirect('subscription:plans')

    else:
        form = SubscriptionPlanForm(instance=plan)
        feature_formset = PlanFeatureFormSet(instance=plan, prefix='features')
        discount_formset = DiscountFormSet(instance=plan, prefix='discounts')

    return render(request, 'super_admin/create_plan.html', {
        'form': form,
        'feature_formset': feature_formset,
        'discount_formset': discount_formset,
        'edit_mode': True
    })

def update_cart_price(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        duration_months = int(data.get('duration_months', 1))
        
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        monthly_price = plan.get_discounted_price(duration_months)
        total_price = plan.get_total_price(duration_months)
        discount = plan.discounts.filter(duration_months=duration_months).first()
        
        response_data = {
            'monthly_price': float(monthly_price),
            'total_price': float(total_price),
            'discount_percentage': float(discount.discount_percentage) if discount else 0,
            'duration_months': duration_months
        }
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def checkout(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        messages.error(request, 'Your cart is empty')
        return redirect('subscription:plans')
    
    cart = get_object_or_404(Cart, id=cart_id)
    
    context = {
        'cart': cart,
        'monthly_price': cart.plan.get_discounted_price(cart.duration_months),
        'total_price': cart.get_total(),
        'discount_percentage': cart.get_discount_percentage(),
        'user_details': cart.user_details
    }
    
    return render(request, 'subscription/checkout.html', context)

# def subscription_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         secret_key = request.POST.get('secret_key')
        
#         try:
#             subscription = SubscriptionUserDetails.objects.get(
#                 email=email,
#                 secret_key=secret_key,
#                 is_active=True
#             )
            
#             # Check if subscription is expired
#             if subscription.subscription_end_date and subscription.subscription_end_date < timezone.now():
#                 messages.error(request, 'Your subscription has expired.')
#                 return redirect('subscription:upgrade_subscription')
            
#             # Store secret key in session
#             request.session['secret_key'] = secret_key
#             return redirect('admin-panel:index')  # Replace with your dashboard URL
            
#         except SubscriptionUserDetails.DoesNotExist:
#             messages.error(request, 'Invalid email or secret key.')
    
#     return render(request, 'subscription/login.html', {})

def index_view(request):
    return render(request,'subscription/index-2.html')

def exceed_view(request):
    return render(request,'subscription/why-choose-exceed.html')

def support_view(request):
    return render(request,'subscription/support.html')


def contact_view(request):
    return render(request,'subscription/contact.html')


def terms_and_conditions(request):
    return render(request,'subscription/terms-and-conditions.html')


def privacy_policy(request):
    return render(request,'subscription/privacy-policy.html')


def refund(request):
    return render(request,'subscription/refund-cancellation.html')


def exceed_cloud_view(request):
    return render(request,'subscription/exceed-cloud.html')

@method_decorator(login_required, name='dispatch')  # Require login
  # Allow anyone to access
def fetch_pricing(request):
    yearly = request.GET.get('yearly', 'false') == 'true'

    plans = SubscriptionPlan.objects.all()
    pricing_data = {}

    for plan in plans:
        monthly_price = float(plan.monthly_price)
        original_price = monthly_price * 12  # Normal yearly price

        # Fetch discount if yearly pricing is requested
        discounted_price = original_price
        discount = SubscriptionDiscount.objects.filter(subscription_plan=plan, duration_months=12).first()
        if discount:
            discount_amount = (original_price * discount.discount_percentage) / 100
            discounted_price = original_price - discount_amount

        pricing_data[plan.id] = {
            "original_price": original_price,
            "discounted_price": discounted_price
        }

    return JsonResponse({"pricing": pricing_data}, status=200)

@login_required
def upgrade_subscription(request, subscription_user_id):
    print("\n=== Debug Information ===")
    print(f"Current user: {request.user}")
    
    # Get current subscription
    current_subscription = get_object_or_404(
        SubscriptionUserDetails, 
        id=subscription_user_id,  # Use the passed subscription_user_id
        user=request.user,  # Fetch subscription details for the logged-in user
        is_active=True
    )
    
    print(f"Current subscription plan: {current_subscription.subscription_plan}")
    
    # Get all available plans except free trial
    available_plans = SubscriptionPlan.objects.filter(
        is_active=True
    ).exclude(
        is_free_trial=True
    ).prefetch_related('plan_features', 'discounts')
    
    if request.method == 'POST':
        form = UpgradeSubscriptionForm(
            request.POST, 
            current_plan=current_subscription.subscription_plan,
            available_plans=available_plans
        )
        if form.is_valid():
            new_plan = form.cleaned_data['plan']
            duration_months = int(form.cleaned_data['duration_months'])
            
            # Check if it's a downgrade
            is_downgrade = float(new_plan.monthly_price) < float(current_subscription.subscription_plan.monthly_price)
            confirm_downgrade = request.POST.get('confirm_downgrade')
            
            if is_downgrade and not confirm_downgrade:
                # Handle downgrade confirmation logic
                return render(request, 'subscription/confirm_downgrade.html', {
                    'current_plan': current_subscription.subscription_plan,
                    'new_plan': new_plan,
                    'duration_months': duration_months,
                    'user_details': current_subscription,
                })
            
            # Calculate remaining time and credit
            remaining_days = (current_subscription.subscription_end_date - timezone.now()).days
            credit = Decimal('0')
            if remaining_days > 0 and not (new_plan.id == current_subscription.subscription_plan.id):
                current_monthly_price = Decimal(str(current_subscription.subscription_plan.monthly_price))
                current_daily_rate = current_monthly_price / Decimal('30')
                remaining_value = current_daily_rate * Decimal(str(remaining_days))
                credit = remaining_value * Decimal('0.60')
            
            # Calculate new subscription cost
            new_price = Decimal(str(new_plan.get_total_price(duration_months)))
            final_amount = max(Decimal('0'), new_price - credit)
            
            print(f"Final amount after credit: {final_amount}")
            
            # Store the final amount in the session for payment processing
            request.session['payment_amount'] = str(final_amount)
            
            # Create cart for upgrade
            cart = Cart.objects.create(
                user_details=current_subscription,
                plan=new_plan,
                duration_months=duration_months
            )
            
            # Store credit information in session for payment processing
            request.session['cart_id'] = cart.id
            request.session['credit_amount'] = str(credit)
            request.session['original_price'] = str(new_price)
            request.session['is_same_plan'] = new_plan.id == current_subscription.subscription_plan.id
            
            # Redirect to create_payment for confirmation
            return redirect('subscription:create_payment')

    else:
        form = UpgradeSubscriptionForm(
            current_plan=current_subscription.subscription_plan,
            available_plans=available_plans
        )
    
    context = {
        'form': form,
        'current_subscription': current_subscription,
        'available_plans': available_plans,
    }
    return render(request, 'subscription/upgrade_subscription.html', context)

@login_required
def subscription_status(request):
    try:
        # Get the latest active subscription for the user
        subscription = get_object_or_404(
            SubscriptionUserDetails.objects.select_related('subscription_plan'),
            user=request.user,
            is_active=True
        )
        
        # Calculate days remaining
        now = timezone.now()
        end_date = subscription.subscription_end_date
        days_remaining = (end_date - now).days if end_date > now else 0
        
        # Get plan features
        features = subscription.subscription_plan.get_feature_list()
        
        context = {
            'subscription': subscription,
            'end_date': end_date,
            'days_remaining': days_remaining,
            'features': features,
            'active_subscription': subscription,  # For the upgrade button condition
            'subscription_user_id': subscription.id  # Pass the subscription_user_id
        }
        
        return render(request, 'subscription/status.html', context)
        
    except SubscriptionUserDetails.DoesNotExist:
        messages.error(request, 'No active subscription found.')
        return redirect('subscription:plans')

# def client_logos_view(request):
#     logos = LogoSettings.objects.select_related('subscription_user').filter(subscription_user__isnull=False)
#     context = {'logos': logos}
#     return render(request, 'your_template.html', context)

# @login_required
def client_view(request):
    subscription_users = SubscriptionUserDetails.objects.select_related('subscription_plan').filter(is_active=True)

    # Map logos to their subscription_user IDs
    logo_map = {
        logo.subscription_user_id: logo
        for logo in LogoSettings.objects.select_related('subscription_user')
        if logo.subscription_user_id is not None
    }

    context = {
        'subscription_users': subscription_users,
        'logo_map': logo_map,
        'client_count': subscription_users.count(),
    }
    return render(request, 'subscription/clients.html', context)

def client_guest_view(request):
    subscription_users = SubscriptionUserDetails.objects.select_related('subscription_plan').filter(is_active=True)

    # Map logos to their subscription_user IDs
    logo_map = {
        logo.subscription_user_id: logo
        for logo in LogoSettings.objects.select_related('subscription_user')
        if logo.subscription_user_id is not None
    }

    context = {
        'subscription_users': subscription_users,
        'logo_map': logo_map,
        'client_count': subscription_users.count(),
    }
    return render(request, 'guest/clients.html',context)


def register_guest(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        proof_type = request.POST.get('proof_type')
        proof_no = request.POST.get('proof_no')
        proof_file = request.FILES.get('proof_file')

        if not all([username, password, name, phone, email]):
            return JsonResponse({'status': False, 'message': 'All fields are required'}, status=400)

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'status': False, 'message': 'Username already exists'}, status=400)

        user = CustomUser.objects.create_user(username=username, password=password, email=email)
        user.is_guest = True
        user.save()

        Guest.objects.create(
            user=user,
            name=name,
            phone=phone,
            email=email,
            address=address,
            proof_type=proof_type,
            proof_no=proof_no,
            proof_file=proof_file,
            subscription_user=getattr(request.user, 'subscriptionuserdetails', None)
        )

        return JsonResponse({
            'status': True,
            'message': 'Guest registered successfully!',
            'redirect_url': reverse('admin-panel:login')
        })

    return render(request, 'hotelapp/guest_form.html')
def send_email_otp(email, request):
    otp = random.randint(100000, 999999)
    request.session['email_otp'] = otp
    request.session['email_to_verify'] = email
    send_mail(
        'Your Email Verification OTP',
        f'Your OTP is {otp}.',
        'no-reply@yourdomain.com',
        [email],
        fail_silently=False
    )

def send_guest_email_otp(request):
    email = request.GET.get('email')
    if email:
        send_email_otp(email, request)
        return JsonResponse({'status': 'sent'})
    return JsonResponse({'status': 'error'}, status=400)


def validate_guest_email_otp(request):
    input_otp = request.GET.get('otp')
    session_otp = str(request.session.get('email_otp'))
    if input_otp == session_otp:
        request.session['email_verified'] = True
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def guest_view(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    bookings = guest.booking_set.all()
    
    context = {
        'guest': guest,
        'bookings': bookings,
    }
    return render(request, 'subscription/guest-details.html', context)


@csrf_exempt  # Use cautiously; better to handle CSRF in JS for security
def contact_form_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # Optional: send email notification to admin
            send_mail(
                subject=f"New Contact Message from {contact.name}",
                message=contact.message,
                from_email=contact.email,
                recipient_list=['support@ultrakeyit.com'],
            )

            return JsonResponse({'success': True, 'message': 'Thank you for contacting us!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)

@csrf_exempt
def update_guest_field(request):
    if request.method == "POST" and request.user.is_authenticated:
        guest = Guest.objects.get(user=request.user)
        form = GuestUpdateForm(request.POST, request.FILES, instance=guest)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': "Guest details updated successfully!"})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': "Unauthorized or invalid request."})



@superuser_required
def guest_list_view(request):
    guests = Guest.objects.all()
    return render(request, 'super_admin/guest_list.html', {'guests': guests})

@method_decorator(superuser_required, name='dispatch')
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'super_admin/bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.select_related('guest', 'room__room_type','subscription_user').order_by('-created_at')
    

# @method_decorator(superuser_required, name='dispatch')
def admin_list(request):
    admin = SubscriptionUserDetails.objects.all()
    return render(request, 'super_admin/admin_list.html', {'admin': admin})


# @method_decorator(superuser_required, name='dispatch')
def superadmin_dashboard_view(request):
    admin = SubscriptionUserDetails.objects.all()

    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_visitors = Guest.objects.count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    total_subscriptions = SubscriptionUserDetails.objects.count()

    today = now().date()
    months = []
    revenues = []
    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        month_label = f"{month_name[month_start.month]} {month_start.year}"
        month_revenue = Booking.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        months.append(month_label)
        revenues.append(month_revenue)

    # Growth percentages (example calculation logic)
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month.replace(day=1)
    last_month_end = last_month + timedelta(days=1)

    current_month_start = today.replace(day=1)

    current_month_bookings = Booking.objects.filter(created_at__gte=current_month_start).count()
    last_month_bookings = Booking.objects.filter(created_at__range=(last_month_start, last_month_end)).count()

    booking_growth = (
        ((current_month_bookings - last_month_bookings) / last_month_bookings) * 100
        if last_month_bookings else 0
    )

    current_month_revenue = Booking.objects.filter(created_at__gte=current_month_start).aggregate(total=Sum('total_amount'))['total'] or 0
    last_month_revenue = Booking.objects.filter(created_at__range=(last_month_start, last_month_end)).aggregate(total=Sum('total_amount'))['total'] or 0

    revenue_growth = (
        ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
        if last_month_revenue else 0
    )

    # Booking Status Breakdown
    status_labels = ['Confirmed', 'Cancelled', 'Pending']
    status_data = [
        Booking.objects.filter(status='confirmed').count(),
        Booking.objects.filter(status='cancelled').count(),
        Booking.objects.filter(status='pending').count(),
    ]

    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'team_members': total_visitors,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'rooms_availability_percent': (available_rooms / total_rooms * 100) if total_rooms else 0,
        'total_subscriptions': total_subscriptions,
        'booking_growth': round(booking_growth, 2),
        'revenue_growth': round(revenue_growth, 2),
        'months': months,
        'revenues': revenues,
        'status_labels': status_labels,
        'status_data': status_data,
        'admin': admin,
    }

    #  # Mock total counts
    # total_bookings = 120
    # total_revenue = 854320.75
    # total_visitors = 340
    # total_rooms = 80
    # available_rooms = 56
    # rooms_availability_percent = (available_rooms / total_rooms) * 100

    # # Mock growth values
    # booking_growth = 12.5
    # revenue_growth = -4.3

    # # Generate mock revenue for past 6 months
    # today = datetime.today().date()
    # months = []
    # revenues = []

    # for i in range(5, -1, -1):
    #     month_date = today.replace(day=1) - timedelta(days=i*30)
    #     month_label = f"{month_name[month_date.month]} {month_date.year}"
    #     months.append(month_label)
    #     revenues.append(random.randint(80000, 160000))

    # # Mock status chart data
    # status_labels = ["Confirmed", "Cancelled", "Pending"]
    # status_data = [random.randint(40, 100), random.randint(5, 30), random.randint(10, 50)]

    # context = {
    #     "total_bookings": total_bookings,
    #     "total_revenue": total_revenue,
    #     "team_members": total_visitors,
    #     "available_rooms": available_rooms,
    #     "total_rooms": total_rooms,
    #     "rooms_availability_percent": round(rooms_availability_percent, 2),
    #     "booking_growth": booking_growth,
    #     "revenue_growth": revenue_growth,
    #     "months": months,
    #     "revenues": revenues,
    #     "status_labels": status_labels,
    #     "status_data": status_data,
    # }

    return render(request, 'super_admin/super_dashboard.html', context)





def get_contact_notifications(request):
    messages = ContactMessage.objects.all().order_by('-created_at')[:10]  # Optional: show latest first
    unread_count = ContactMessage.objects.filter(is_read=False).count()

    notifications = []
    for msg in messages:
        notifications.append({
            'sender': msg.name,
            'message': msg.message,
            'time': naturaltime(msg.created_at),
        })

    return JsonResponse({'notifications': notifications, 'unread_count': unread_count})


@csrf_exempt
@require_POST
def mark_contact_notifications_read(request):
    
    ContactMessage.objects.filter( is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


def tax_add_view(request):
    taxes = Tax.objects.all()

    if request.method == 'POST':
        form = TaxForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tax added successfully.')
            return redirect('subscription:tax_add_view')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaxForm()

    return render(request, 'super_admin/tax_add.html', {'form': form, 'taxes': taxes})

@csrf_exempt
def delete_tax(request):
    if request.method == 'POST':
        tax_id = request.POST.get('id')
        try:
            tax = Tax.objects.get(id=tax_id)
            tax.delete()
            return JsonResponse({'success': True, 'message': 'Tax deleted successfully'})
        except Tax.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Tax not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@require_POST
def edit_tax(request):
    tax_id = request.POST.get('id')
    name = request.POST.get('name')
    percentage = request.POST.get('percentage')
    is_platform_fee = request.POST.get('is_platform_fee') == 'true'

    try:
        tax = Tax.objects.get(id=tax_id)
        tax.name = name
        tax.percentage = percentage
        tax.is_platform_fee = is_platform_fee
        tax.save()
        return JsonResponse({'success': True, 'message': 'Tax updated successfully.'})
    except Tax.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tax not found.'})




