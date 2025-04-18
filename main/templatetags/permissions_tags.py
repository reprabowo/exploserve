# main/templatetags/permission_tags.py

from django import template
from main.permissions import (
    can_manage_user as can_manage_user_logic,
    can_delete_user as can_delete_user_logic,
)

register = template.Library()

@register.filter(name='can_manage_user')
def can_manage_user_filter(manager, target):
    return can_manage_user_logic(manager, target)

@register.filter(name='can_delete_user')
def can_delete_user_filter(manager, target):
    return can_delete_user_logic(manager, target)
