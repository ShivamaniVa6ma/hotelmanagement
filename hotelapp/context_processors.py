from subscription.models import SubscriptionUserDetails
from .models import LogoSettings


def get_active_subscription(request):
    """
    Simple context processor that always returns a dictionary
    with subscription information
    """
    print("Context processor called")
    # Default context dictionary
    context_dict = {
        'active_subscription': None,
        'has_subscription': False,
        'subscription_plan': None,
        'company_name': None,
        'is_authenticated': request.user.is_authenticated
    }
    
    # Only proceed if user is authenticated
    if not request.user.is_authenticated:
        return context_dict
    
    try:
        # Get subscription ID from session
        subscription_id = request.session.get('active_subscription_id')
        
        # Try to get the subscription
        if subscription_id:
            subscription = SubscriptionUserDetails.objects.filter(
                id=subscription_id,
                user=request.user,
                is_active=True
            ).select_related('subscription_plan').first()
        else:
            # If no subscription ID in session, get the first active subscription
            subscription = SubscriptionUserDetails.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('subscription_plan').first()
            
            # If found, store in session
            if subscription:
                request.session['active_subscription_id'] = subscription.id
        
        # Update context if subscription exists
        if subscription and subscription.subscription_plan:
            context_dict.update({
                'active_subscription': subscription,
                'has_subscription': True,
                'subscription_plan': subscription.subscription_plan,
                'company_name': subscription.company_name
            })
    
    except Exception as e:
        print(f"Error in context processor: {str(e)}")
        # Keep using default context in case of error
    
    print(f"Returning context: {context_dict}")
    # Always return the dictionary
    return context_dict


def dynamic_logos(request):
    if request.user.is_authenticated:
        # Get the user's subscription details
        subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()
        
        # Fetch the logo settings for the subscription user
        logo_settings = LogoSettings.objects.filter(subscription_user=subscription_user).first() if subscription_user else None

        return {
            "site_name": logo_settings.site_name if logo_settings and logo_settings.site_name else "Default Site Name",

            "favicon_url": logo_settings.favicon.url if logo_settings and logo_settings.favicon else None,
            "light_logo_url": logo_settings.light_logo.url if logo_settings and logo_settings.light_logo else None,
            "dark_logo_url": logo_settings.dark_logo.url if logo_settings and logo_settings.dark_logo else None,
        }
    return {}