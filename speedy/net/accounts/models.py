import uuid

from django.apps import apps
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

ACCESS_ME = 1
ACCESS_FRIENDS = 2
ACCESS_FRIENDS_2 = 3
ACCESS_ANYONE = 4

ACCESS_CHOICES = (
    (ACCESS_ME, _('Only me')),
    (ACCESS_FRIENDS, _('Me and my friends')),
    (ACCESS_FRIENDS_2, _('Me, my friends and friends of my friends')),
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

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})

    @property
    def profile(self):
        if not hasattr(self, '_profile'):
            model = apps.get_model(*settings.AUTH_PROFILE_MODEL.split('.'))
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


class BaseSiteProfile(TimeStampedModel):
    """
    SiteProfile contains site-specific user settings.
    """

    class Meta:
        abstract = True

    user = models.OneToOneField(User, primary_key=True, related_name='+')
    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to Speedy Net'),
                                    default=False)

    def __str__(self):
        return '{} @ {}'.format(self.user, settings.SITE_NAME)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})


class SiteProfile(BaseSiteProfile):
    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    access_account = AccessField(verbose_name=_('who can view my account'), default=ACCESS_ANYONE)
    public_email = models.ForeignKey(UserEmailAddress, verbose_name=_('public email'), blank=True, null=True,
                                     limit_choices_to={'is_confirmed': True}, on_delete=models.SET_NULL,
                                     related_name='+')
