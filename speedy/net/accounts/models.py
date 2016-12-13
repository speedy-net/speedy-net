import re
import uuid
from datetime import datetime, date

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from speedy.core.mail import send_mail
from speedy.core.models import TimeStampedModel, SmallUDIDField, generate_confirmation_token, RegularUDIDField
from speedy.net.uploads.fields import PhotoField
from .managers import UserManager
from .utils import get_site_profile_model
from .validators import get_username_validators, get_slug_validators

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


def normalize_slug(slug):
    slug = slug.lower()
    slug = re.sub('[^a-zA-Z0-9]{1,}', '-', slug)
    slug = re.sub('^-', '', slug)
    slug = re.sub('-$', '', slug)
    return slug


def normalize_username(slug):
    slug = normalize_slug(slug)
    username = re.sub('[-\._]', '', slug)
    return username


class Entity(TimeStampedModel):
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 120
    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200

    id = SmallUDIDField()
    username = models.CharField(verbose_name=_('username'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    slug = models.CharField(verbose_name=_('username (slug)'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    photo = PhotoField(verbose_name=_('photo'), blank=True, null=True)

    validators = {
        'username': get_username_validators(min_length=MIN_USERNAME_LENGTH, max_length=MAX_USERNAME_LENGTH, allow_letters_after_digits=True),
        'slug': get_slug_validators(min_length=MIN_SLUG_LENGTH, max_length=MAX_SLUG_LENGTH, allow_letters_after_digits=True),
    }

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entity')
        ordering = ('id',)

    def __str__(self):
        return '<Entity {}>'.format(self.id)

    def save(self, *args, **kwargs):
        self.slug = normalize_slug(self.slug)
        self.username = normalize_username(self.username)
        return super().save(*args, **kwargs)

    def validate_username_for_slug(self):
        if normalize_username(self.slug) != self.username:
            raise ValidationError(_('Slug does not parse to username.'))

    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        try:
            super().clean_fields(exclude=exclude)
        except ValidationError as e:
            errors = e.error_dict
        else:
            errors = {}

        self.slug = normalize_slug(self.slug)
        if self.username:
            self.username = normalize_username(self.username)
        else:
            self.username = normalize_username(self.slug)

        username_exists = Entity.objects.filter(username=self.username).exclude(id=self.id).exists()
        if username_exists:
            errors['slug'] = [self._meta.get_field('slug').error_messages['unique']]
            # errors['username'] = [self._meta.get_field('username').error_messages['unique']]

        for field_name, validators in self.validators.items():
            f = self._meta.get_field(field_name)
            if field_name in exclude:
                pass
            else:
                raw_value = getattr(self, f.attname)
                if f.blank and raw_value in f.empty_values:
                    pass
                else:
                    for v in validators:
                        try:
                            v(raw_value)
                            if field_name == 'slug' and self.username:
                                self.validate_username_for_slug()
                        except ValidationError as e:
                            errors[f.name] = [e.error_list[0].messages[0]]
        if errors:
            raise ValidationError(errors)


class NamedEntity(Entity):
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 200

    name = models.CharField(verbose_name=_('name'), max_length=255)

    def __str__(self):
        return '<NamedEntity {} - {}>'.format(self.id, self.name)


class User(Entity, PermissionsMixin, AbstractBaseUser):
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 40
    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 120

    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDER_OTHER = 3
    GENDER_CHOICES = (
        (GENDER_FEMALE, _('Female')),
        (GENDER_MALE, _('Male')),
        (GENDER_OTHER, _('Other')),
    )

    DIET_UNKNOWNN   = 0
    DIET_VEGAN      = 1
    DIET_VEGETARIAN = 2
    DIET_CARNIST    = 3
    DIET_CHOICES = (
        (DIET_UNKNOWNN, _('Please select...')),
        (DIET_VEGAN, _('Vegan (eats only plants and fungi)')),
        (DIET_VEGETARIAN, _('Vegetarian (doesn\'t eat fish and meat)')),
        (DIET_CARNIST, _('Carnist (eats animals)'))
    )

    USERNAME_FIELD = 'username'

    first_name = models.CharField(verbose_name=_('first name'), max_length=75)
    last_name = models.CharField(verbose_name=_('last name'), max_length=75)
    date_of_birth = models.DateField(verbose_name=_('date of birth'))
    gender = models.SmallIntegerField(verbose_name=_('I am'), choices=GENDER_CHOICES)
    diet = models.SmallIntegerField(verbose_name=_('diet'), choices=DIET_CHOICES, default=DIET_UNKNOWNN)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    validators = {
        'username': get_username_validators(min_length=MIN_USERNAME_LENGTH, max_length=MAX_USERNAME_LENGTH, allow_letters_after_digits=False),
        'slug': get_slug_validators(min_length=MIN_SLUG_LENGTH, max_length=MAX_SLUG_LENGTH, allow_letters_after_digits=False),
    }

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-last_login', 'id')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse('profiles:user', kwargs={'slug': self.slug})

    @property
    def email(self):
        try:
            return self.email_addresses.get(is_primary=True).email
        except UserEmailAddress.DoesNotExist:
            return None

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

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    @property
    def profile(self):
        if not hasattr(self, '_profile'):
            model = get_site_profile_model()
            self._profile = model.objects.get_or_create(user=self)[0]
        return self._profile


class UserEmailAddress(TimeStampedModel):
    id = RegularUDIDField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name='email_addresses')
    email = models.EmailField(verbose_name=_('email'), unique=True)
    is_confirmed = models.BooleanField(verbose_name=_('is confirmed'), default=False)
    is_primary = models.BooleanField(verbose_name=_('is primary'), default=False)
    confirmation_token = models.CharField(verbose_name=_('confirmation token'), max_length=32, blank=True)
    confirmation_sent = models.IntegerField(verbose_name=_('confirmation sent'), default=0)
    access = AccessField(verbose_name=_('who can see this email'), default=ACCESS_ME)

    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')
        ordering = ('date_created', 'id', )

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.confirmation_token:
            self.confirmation_token = self._generate_confirmation_token()
        return super().save(*args, **kwargs)

    def _generate_confirmation_token(self):
        return generate_confirmation_token()

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

    user = models.OneToOneField(User, primary_key=True, related_name='+')
    last_visit = models.DateTimeField(_('last visit'), auto_now_add=True)
    is_active = True

    class Meta:
        abstract = True

    def __str__(self):
        site = Site.objects.get_current()
        return '{} @ {}'.format(self.user, site.name)

    def update_last_visit(self):
        self.last_visit = now()
        self.save(update_fields={'last_visit'})

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()


class SiteProfile(SiteProfileBase):
    class Meta:
        verbose_name = 'Speedy Net Profile'
        verbose_name_plural = 'Speedy Net Profiles'

    access_account = ACCESS_ANYONE
    access_dob_day_month = AccessField(verbose_name=_('who can view my birth month and day'), default=ACCESS_ME)
    access_dob_year = AccessField(verbose_name=_('who can view my birth year'), default=ACCESS_ME)
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    is_active = models.BooleanField(verbose_name=_('indicates if a user has ever logged in to the site'), default=False)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    def deactivate(self):
        self.is_active = False
        self.save(update_fields={'is_active'})
