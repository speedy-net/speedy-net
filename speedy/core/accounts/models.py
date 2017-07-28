from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from speedy.core.accounts.validators import get_username_validators, get_slug_validators
from speedy.core.base.mail import send_mail
from speedy.core.base.models import TimeStampedModel, SmallUDIDField, RegularUDIDField
from speedy.core.base.utils import normalize_username, normalize_slug, generate_confirmation_token, get_age
from speedy.core.uploads.fields import PhotoField
from .managers import EntityManager, UserManager
from .utils import get_site_profile_model


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

    objects = EntityManager()

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entity')
        ordering = ('id',)

    def __str__(self):
        return '<Entity {}>'.format(self.id)

    def save(self, *args, **kwargs):
        self.slug = normalize_slug(slug=self.slug)
        self.username = normalize_username(slug=self.username)
        return super().save(*args, **kwargs)

    def validate_username_for_slug(self):
        if normalize_username(slug=self.slug) != self.username:
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

        self.slug = normalize_slug(slug=self.slug)
        if self.username:
            self.username = normalize_username(slug=self.username)
        else:
            self.username = normalize_username(slug=self.slug)

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

    class Meta:
        abstract = True

    def __str__(self):
        return '<NamedEntity {} - {}>'.format(self.id, self.name)


class UserAccessField(models.PositiveIntegerField):
    ACCESS_ME = 1
    ACCESS_FRIENDS = 2
    ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS = 3
    ACCESS_ANYONE = 4

    ACCESS_CHOICES = (
        (ACCESS_ME, _('Only me')),
        (ACCESS_FRIENDS, _('Me and my friends')),
        # (ACCESS_FRIENDS_AND_FRIENDS_OF_FRIENDS, _('Me, my friends and friends of my friends')),
        (ACCESS_ANYONE, _('Anyone')),
    )

    def __init__(self, **kwargs):
        kwargs.update({
            'choices': self.ACCESS_CHOICES,
        })
        super().__init__(**kwargs)


class User(Entity, PermissionsMixin, AbstractBaseUser):
    MIN_USERNAME_LENGTH = 6
    MAX_USERNAME_LENGTH = 40
    MIN_SLUG_LENGTH = 6
    MAX_SLUG_LENGTH = 200
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 120

    GENDER_UNKNOWN = 0
    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDER_OTHER = 3
    GENDER_MAX_VALUE_PLUS_ONE = 4
    GENDER_CHOICES = (
        (GENDER_FEMALE, _('Female')),
        (GENDER_MALE, _('Male')),
        (GENDER_OTHER, _('Other')),
    )

    DIET_UNKNOWN = 0
    DIET_VEGAN = 1
    DIET_VEGETARIAN = 2
    DIET_CARNIST = 3
    DIET_MAX_VALUE_PLUS_ONE = 4
    DIET_CHOICES = (
        (DIET_UNKNOWN, _('Please select...')),
        (DIET_VEGAN, _('Vegan (eats only plants and fungi)')),
        (DIET_VEGETARIAN, _('Vegetarian (doesn\'t eat fish and meat)')),
        (DIET_CARNIST, _('Carnist (eats animals)'))
    )

    NOTIFICATIONS_OFF = 0
    NOTIFICATIONS_ON = 1

    NOTIFICATIONS_CHOICES = (
        (NOTIFICATIONS_ON, _('Notify me')),
        (NOTIFICATIONS_OFF, _('Don\'t notify me')),
    )

    USERNAME_FIELD = 'username'

    first_name = models.CharField(verbose_name=_('first name'), max_length=75)
    last_name = models.CharField(verbose_name=_('last name'), max_length=75)
    date_of_birth = models.DateField(verbose_name=_('date of birth'))
    gender = models.SmallIntegerField(verbose_name=_('I am'), choices=GENDER_CHOICES)
    diet = models.SmallIntegerField(verbose_name=_('diet'), choices=DIET_CHOICES, default=DIET_UNKNOWN)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    access_dob_day_month = UserAccessField(verbose_name=_('who can view my birth month and day'), default=UserAccessField.ACCESS_ME)
    access_dob_year = UserAccessField(verbose_name=_('who can view my birth year'), default=UserAccessField.ACCESS_ME)
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=NOTIFICATIONS_CHOICES, default=NOTIFICATIONS_ON)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth', 'gender', 'diet', 'slug']

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
        # Depends on site: full name in Speedy Net, first name in Speedy Match.
        return self.profile.get_name()

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
            return addresses[0].mail(template_name_prefix=template_name_prefix, context=context)
        return False

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name).strip() or self.slug

    def get_first_name(self):
        return '{}'.format(self.first_name).strip() or self.slug

    def get_short_name(self):
        return self.get_first_name()

    def has_confirmed_email(self):
        return self.email_addresses.filter(is_confirmed=True).exists()

    @cached_property
    def has_verified_email(self):
        return self.has_confirmed_email() or self.date_created > now() - timedelta(hours=2)

    def activate(self):
        self.is_active = True
        self.save(update_fields={'is_active'})

    @property
    def profile(self):
        if not hasattr(self, '_profile'):
            self._profile = self.get_profile()
        return self._profile

    def get_profile(self, model=None, profile_model=None) -> 'SiteProfileBase':
        if model is None:
            model = get_site_profile_model(profile_model=profile_model)
        return model.objects.get_or_create(user=self)[0]

    def get_gender(self):
        genders = {self.__class__.GENDER_FEMALE: 'female', self.__class__.GENDER_MALE: 'male', self.__class__.GENDER_OTHER: 'other'}
        return genders.get(self.gender)

    def get_gender_translated(self):
        genders = {self.__class__.GENDER_FEMALE: _('female'), self.__class__.GENDER_MALE: _('male'), self.__class__.GENDER_OTHER: _('other')}
        return genders.get(self.gender)

    def get_diet(self):
        diets = {self.__class__.DIET_VEGAN: pgettext_lazy(context=self.get_gender(), message='Vegan'), self.__class__.DIET_VEGETARIAN: pgettext_lazy(context=self.get_gender(), message='Vegetarian'), self.__class__.DIET_CARNIST: pgettext_lazy(context=self.get_gender(), message='Carnist')}
        return diets.get(self.diet)

    def get_age(self):
        return get_age(date_birth=self.date_of_birth)

    def get_diet_choices(self):
        return (
            (self.__class__.DIET_VEGAN, pgettext_lazy(context=self.get_gender(), message='Vegan (eats only plants and fungi)')),
            (self.__class__.DIET_VEGETARIAN, pgettext_lazy(context=self.get_gender(), message='Vegetarian (doesn\'t eat fish and meat)')),
            (self.__class__.DIET_CARNIST, pgettext_lazy(context=self.get_gender(), message='Carnist (eats animals)'))
        )


class UserEmailAddress(TimeStampedModel):
    id = RegularUDIDField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name='email_addresses')
    email = models.EmailField(verbose_name=_('email'), unique=True)
    is_confirmed = models.BooleanField(verbose_name=_('is confirmed'), default=False)
    is_primary = models.BooleanField(verbose_name=_('is primary'), default=False)
    confirmation_token = models.CharField(verbose_name=_('confirmation token'), max_length=32, blank=True)
    confirmation_sent = models.IntegerField(verbose_name=_('confirmation sent'), default=0)
    access = UserAccessField(verbose_name=_('who can see this email'), default=UserAccessField.ACCESS_ME)

    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')
        ordering = ('date_created', 'id',)

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
        if hasattr(self.user.profile, 'validate_profile_and_activate') and UserEmailAddress.objects.filter(user=self.user_id, is_confirmed=True).count() == 1:
            self.user.profile.activation_step = len(settings.SITE_PROFILE_FORM_FIELDS)
            self.user.profile.validate_profile_and_activate()
            self.user.profile.activation_step = 2
            self.user.profile.save(update_fields=['activation_step'])

    def make_primary(self):
        self.user.email_addresses.update(is_primary=False)
        self.is_primary = True
        self.save(update_fields={'is_primary'})


class SiteProfileBase(TimeStampedModel):
    """
    SiteProfile contains site-specific user settings.
    """

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

    def get_name(self):
        raise NotImplementedError()

