from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from base.models import (UserProfile, UserEmailAddress)


class AuthBackend(object):
    def authenticate(self, email=None, username=None, password=None):
        if username:
            user = self.get_user_by_username(username)
        if email:
            user = self.get_user_by_email(email)

        if not user:
            return None

        if password and user and user.check_password(password):
            return user
        return None

    def get_user(self, id=None, username=None):
        if not id or not username:
            return None
        if username:
            return self.get_user_by_username(username)
        profile = (None,)
        if not id:
            return None

        try:
            profile = UserProfile.objects.get(identity__id=id)
        except ObjectDoesNotExist as e:
            return None
        return profile.user

    def get_user_by_username(self, username):
        try:
            profile = UserProfile.objects.get(identity__username=username)
        except:
            return None
        return profile.user

    def get_user_by_email(self, email):
        try:
            email = UserEmailAddress.objects.get(email=email)
        except ObjectDoesNotExist as e:
            return None
        return email.profile.user
