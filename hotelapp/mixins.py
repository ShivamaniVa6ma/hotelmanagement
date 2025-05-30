from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class SubscriptionRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.check_subscription_status()

    def handle_no_permission(self):
        messages.warning(self.request, "Please upgrade your subscription to access this feature.")
        return redirect('subscription:plans') 