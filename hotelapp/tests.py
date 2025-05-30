from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from .context_processors import get_active_subscription

# Create your tests here.

class ContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_context_processor_returns_dict(self):
        request = self.factory.get('/')
        request.user = self.user
        context = get_active_subscription(request)
        self.assertIsInstance(context, dict)
        self.assertIn('active_subscription', context)
        self.assertIn('has_subscription', context)
