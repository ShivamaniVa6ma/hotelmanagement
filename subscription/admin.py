from django.contrib import admin
from .models import SubscriptionPlan, PlanFeature, Payment, SubscriptionUserDetails

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_price', 'is_popular', 'is_active')
    list_filter = ('is_popular', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('monthly_price',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['features'].help_text = 'Enter features as a list of strings'
        return form

@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('plan', 'feature_text', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('feature_text',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user_details', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user_details__name', 'order_id', 'payment_id')

@admin.register(SubscriptionUserDetails)
class SubscriptionUserDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'company_name', 'email', 'phone')
    list_filter = ('created_at',)


