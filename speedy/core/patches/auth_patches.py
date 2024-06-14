def patch():
    from django.contrib.auth import get_user_model
    from django.contrib.auth.backends import ModelBackend
    from django.contrib.auth.hashers import make_password

    UserModel = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Patch: Replace call to User.set_password with make_password.
            # https://code.djangoproject.com/ticket/35492
            make_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    ModelBackend.authenticate = authenticate
