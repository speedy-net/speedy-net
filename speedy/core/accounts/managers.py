from django.db.models import Q

from speedy.core.base.models import BaseManager, BaseUserManager
from speedy.core.base.utils import normalize_username
from speedy.core.accounts.utils import get_site_profile_model


class EntityManager(BaseManager):
    def get_by_username(self, username):
        return self.get(username=normalize_username(slug=username))

    def get_by_slug(self, slug):
        return self.get_by_username(username=slug)


class UserManager(BaseUserManager):
    def get_queryset(self):
        site_profile_model = get_site_profile_model()
        return super().get_queryset().select_related(site_profile_model.RELATED_NAME)

    def get_by_natural_key(self, username):
        return self.distinct().get(Q(username=normalize_username(slug=username)) | Q(email_addresses__email=username))

    def active(self, *args, **kwargs):
        return self.filter(is_active=True, *args, **kwargs)

    def _create_user(self, slug, password, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        extra_fields.setdefault('gender', self.model.GENDER_OTHER)
        if (not (slug)):
            raise ValueError('The given username must be set.')
        user = self.model(slug=slug, **extra_fields)
        user.set_password(raw_password=password)
        user.save(using=self._db)
        return user

    def create_user(self, slug, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(slug=slug, password=password, **extra_fields)

    def create_superuser(self, slug, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if (extra_fields.get('is_staff') is not True):
            raise ValueError('Superuser must have is_staff=True.')
        if (extra_fields.get('is_superuser') is not True):
            raise ValueError('Superuser must have is_superuser=True.')

        user = self._create_user(slug=slug, password=password, **extra_fields)
        return user


