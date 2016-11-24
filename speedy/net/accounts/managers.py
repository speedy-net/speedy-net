from django.contrib.auth.models import BaseUserManager
from django.db.models import Q


class UserManager(BaseUserManager):

    def get_by_natural_key(self, username):
        from .models import normalize_username
        return self.distinct().get(Q(username=normalize_username(username)) | Q(email_addresses__email=username))

    def active(self):
        return self.filter(is_active=True)

    def _create_user(self, slug, password, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        extra_fields.setdefault('gender', self.model.GENDER_OTHER)
        if not slug:
            raise ValueError('The given username must be set')
        user = self.model(slug=slug, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, slug, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(slug, password, **extra_fields)

    def create_superuser(self, slug, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(slug, password, **extra_fields)
