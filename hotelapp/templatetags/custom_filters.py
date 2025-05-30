# hotelapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def percentage_of(value, max_value):
    try:
        return (float(value) / float(max_value)) * 100
    except (ValueError, ZeroDivisionError):
        return 0