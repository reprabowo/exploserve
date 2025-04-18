# main/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Authentication backend that allows users to log in with their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Here, we use the 'username' parameter as the email.
        # Alternatively, you could check for 'email' in kwargs.
        if username is None:
            username = kwargs.get('email')
        try:
            # Try to fetch the user by email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            # Check the password and if the user is active.
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
