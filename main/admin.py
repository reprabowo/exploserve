from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

# Define a new User admin that includes the Profile inline
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# Unregister the default User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

