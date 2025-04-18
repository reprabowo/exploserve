from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def container_class(context):
    user = context.get('user')
    if user and user.is_authenticated:
        try:
            role = user.profile.role
            if role in ["system_owner", "system_admin", "institution_admin"]:
                return "container mt-4 with-sidebar"
        except Exception:
            pass
    return "container mt-4"
