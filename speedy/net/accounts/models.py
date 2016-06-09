import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.mail import send_mail
from speedy.core.models import TimeStampedModel
from .managers import UserManager
from .utils import generate_id
from .validators import identity_id_validator

USER_PRIVATE_FIELD = 1
USER_FRIENDS_FIELD = 2
USER_PUBLIC_FIELD = 3
DEFAULT_USER_FIELD_PRIVACY = {
    'first_name': USER_PRIVATE_FIELD,
    'last_name': USER_PRIVATE_FIELD,
    'gender': USER_PRIVATE_FIELD,
    'diet': USER_PRIVATE_FIELD,
    'email': USER_PRIVATE_FIELD,
    'date_of_birth': USER_PRIVATE_FIELD
}


class Entity(TimeStampedModel):
    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entity')

    id = models.CharField(max_length=15, validators=[identity_id_validator], primary_key=True, db_index=True,
                          unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_id()
            while Entity.objects.filter(id=self.id).exists():
                self.id = generate_id()
        if not self.slug:
            self.slug = self.id
        return super().save(*args, **kwargs)

    def __str__(self):
        return '<Entity {}>'.format(self.id)


class User(Entity, PermissionsMixin, AbstractBaseUser):
    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDER_OTHER = 3
    GENDER_CHOICES = (
        (GENDER_MALE, _('Male')),
        (GENDER_FEMALE, _('Female')),
        (GENDER_OTHER, _('Other')),
    )
    USERNAME_FIELD = 'slug'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    first_name = models.CharField(verbose_name=_('first name'), max_length=75)
    last_name = models.CharField(verbose_name=_('last name'), max_length=75)
    date_of_birth = models.DateField(verbose_name=_('date of birth'), blank=True, null=True)
    gender = models.SmallIntegerField(verbose_name=_('gender'), choices=GENDER_CHOICES)
    profile_picture = models.ImageField(verbose_name=_('profile picture'), upload_to='accounts/user/profile_picture/',
                                        blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    @property
    def email(self):
        return self.email_addresses.get(is_primary=True).email

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def has_confirmed_email(self):
        return self.email_addresses.filter(is_confirmed=True).exists()

    def get_absolute_url(self):
        return reverse('accounts:user_profile', kwargs={'slug': self.slug})

    def __str__(self):
        return self.get_full_name()


class UserEmailAddress(TimeStampedModel):
    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name='email_addresses')
    email = models.EmailField(verbose_name=_('email'), unique=True)
    is_confirmed = models.BooleanField(verbose_name=_('is confirmed'), default=False)
    is_primary = models.BooleanField(verbose_name=_('is primary'), default=False)
    confirmation_token = models.CharField(verbose_name=_('confirmation token'), max_length=32, blank=True)

    def save(self, *args, **kwargs):
        if not self.confirmation_token:
            self.confirmation_token = self._generate_confirmation_token()
        return super().save(*args, **kwargs)

    @staticmethod
    def _generate_confirmation_token():
        return uuid.uuid4().hex

    def mail(self, template_name_prefix, context=None):
        context = context or {}
        context.update({
            'email_address': self,
            'user': self.user,
        })
        return send_mail([self.email], template_name_prefix, context)

    def send_confirmation_email(self):
        return self.mail('accounts/email/verify_email')

    def verify(self):
        self.is_confirmed = True
        self.save(update_fields={'is_confirmed'})

    def make_primary(self):
        self.user.email_addresses.update(is_primary=False)
        self.is_primary = True
        self.save(update_fields={'is_primary'})

    def __str__(self):
        return self.email
