# myapp/templatetags/phone_filters.py
from django import template

register = template.Library()

@register.filter
def whatsapp_link(phone_number):
    """
    Removes the leading '0' (if present) from a phone number
    then prepends '62' and returns the complete WhatsApp URL.
    """
    if phone_number.startswith('0'):
        phone_number = phone_number[1:]  # remove leading '0'
    return f"https://wa.me/62{phone_number}"
