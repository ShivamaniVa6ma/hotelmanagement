from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils import timezone
import random
import string
class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, timezone.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

def custom_json_response(data, safe=True, **kwargs):
    """
    Custom JSON response that uses CustomJSONEncoder
    """
    kwargs['encoder'] = CustomJSONEncoder
    return JsonResponse(data, safe=safe, **kwargs)

def generate_invoice_id():
    return "INV" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
