import uuid
import re

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from speedy.core.mail import send_mail
from speedy.core.models import TimeStampedModel
from speedy.net.uploads.fields import PhotoField
from .managers import UserManager
from .utils import generate_id, get_site_profile_model
from .validators import identity_id_validator, username_validator

ACCESS_ME = 1
ACCESS_FRIENDS = 2
ACCESS_FRIENDS_2 = 3
ACCESS_ANYONE = 4

ACCESS_CHOICES = (
    (ACCESS_ME, _('Only me')),
    (ACCESS_FRIENDS, _('Me and my friends')),
    # (ACCESS_FRIENDS_2, _('Me, my friends and friends of my friends')),
    (ACCESS_ANYONE, _('Anyone')),
)


class AccessField(models.PositiveIntegerField):
    def __init__(self, **kwargs):
        kwargs.update({
            'choices': ACCESS_CHOICES,
        })
        super().__init__(**kwargs)


class Entity(TimeStampedModel):
    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entity')

    id = models.CharField(max_length=15, validators=[identity_id_validator], primary_key=True, db_index=True,
                          unique=True)
    username = models.CharField(max_length=20, validators=[username_validator], unique=True)
    slug = models.SlugField(unique=True)
    photo = PhotoField(verbose_name=_('photo'), blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_id()
            while Entity.objects.filter(id=self.id).exists():
                self.id = generate_id()
        if not self.slug:
            self.slug = self.id
        self.slug = re.sub('[-]{1,}', '-', self.slug)
        self.slug = re.sub('^-', '', self.slug)
        self.slug = re.sub('-$', '', self.slug)
        if not self.username:
            self.username = re.sub('[-]', '', self.slug)
        if re.sub('[-]', '', self.slug) != self.username:
            raise ValidationError('slug does not parse to username.')
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
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    @property
    def email(self):
        return self.email_addresses.get(is_primary=True).email

    def mail_user(self, template_name_prefix, context=None, send_to_unconfirmed=False):
        addresses = self.email_addresses.filter(is_primary=True)
        if not send_to_unconfirmed:
            addresses = addresses.filter(is_confirmed=True)
        addresses = list(addresses)
        if addresses:
            return addresses[0].mail(template_name_prefix, context)
        return False

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name).strip() or self.slug

    def get_short_name(self):
        return self.get_full_name()

    def has_confirmed_email(self):
        return self.email_addresses.filter(is_confirmed=True).exists()

    def get_absolute_url(self):
        return reverse('profiles:user', kwargs={'username': self.slug})

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})

    @property
    def profile(self):
        if not hasattr(self, '_profile'):
            model = get_site_profile_model()
            self._profile = model.objects.get_or_create(user=self)[0]
        return self._profile

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
    confirmation_sent = models.IntegerField(verbose_name=_('confirmation sent'), default=0)

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
        msg_count = self.mail('accounts/email/verify_email')
        self.confirmation_sent += 1
        self.save(update_fields={'confirmation_sent'})
        return msg_count

    def verify(self):
        self.is_confirmed = True
        self.save(update_fields={'is_confirmed'})

    def make_primary(self):
        self.user.email_addresses.update(is_primary=False)
        self.is_primary = True
        self.save(update_fields={'is_primary'})

    def __str__(self):
        return self.email


class SiteProfileBase(TimeStampedModel):
    """
    SiteProfile contains site-specific user settings.
    """

    NOTIFICATIONS_OFF = 0
    NOTIFICATIONS_ON = 1

    NOTIFICATIONS_CHOICES = (
        (NOTIFICATIONS_ON, _('Notify')),
        (NOTIFICATIONS_OFF, _('Don\'t notify')),
    )

    class Meta:
        abstract = True

    user = models.OneToOneField(User, primary_key=True, related_name='+')
    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'),
                                    default=False)

    def __str__(self):
        site = Site.objects.get_current()
        return '{} @ {}'.format(self.user, site.name)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})


class SiteProfile(SiteProfileBase):
    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    access_account = AccessField(verbose_name=_('who can view my account'), default=ACCESS_ANYONE)
    public_email = models.ForeignKey(UserEmailAddress, verbose_name=_('public email'), blank=True, null=True,
                                     on_delete=models.SET_NULL, related_name='+')
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'),
                                                    choices=SiteProfileBase.NOTIFICATIONS_CHOICES,
                                                    default=SiteProfileBase.NOTIFICATIONS_ON)
