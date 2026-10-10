def patch():
    """
    Monkey patch ModelBackend.authenticate to replace the call to User.set_password with make_password, avoiding an unnecessary database save.

    See https://code.djangoproject.com/ticket/35492
    """
    from django.contrib.auth import get_user_model
    from django.contrib.auth.backends import ModelBackend
    from django.contrib.auth.hashers import make_password

    UserModel = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user by username and password, replacing the call to User.set_password (on a non-existing user, to mitigate timing attacks) with make_password.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param username: The username to authenticate with.
        :type username: str
        :param password: The password to authenticate with.
        :type password: str
        :param kwargs: Additional credentials; used to look up the username by ``UserModel.USERNAME_FIELD`` if username is None.
        :return: The authenticated user, or None if authentication failed.
        :rtype: django.contrib.auth.models.AbstractUser or None
        """
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username=username)
        except UserModel.DoesNotExist:
            # Patch: Replace call to User.set_password with make_password.
            # https://code.djangoproject.com/ticket/35492
            make_password(password=password)
        else:
            if user.check_password(raw_password=password) and self.user_can_authenticate(user):
                return user

    ModelBackend.authenticate = authenticate


