import logging
import warnings
from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.urls import reverse
from django.db import models, transaction
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.functional import classproperty, cached_property
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.contrib.sites.models import Site

from translated_fields import TranslatedField

from speedy.core.base.mail import send_mail
from speedy.core.base.managers import BaseManager
from speedy.core.base.models import TimeStampedModel
from speedy.core.base.fields import SmallUDIDField, RegularUDIDField
from speedy.core.base.utils import normalize_slug, normalize_username, generate_confirmation_token, get_age, string_is_not_none, to_attribute, get_all_field_names
from speedy.core.uploads.fields import PhotoField
from .managers import EntityManager, UserManager
from .fields import UserAccessField
from .utils import get_site_profile_model, normalize_email
from . import validators as speedy_core_accounts_validators

logger = logging.getLogger(__name__)


class CleanAndValidateAllFieldsMixin(object):
    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        if (exclude is None):
            exclude = []

        self.clean_all_fields(exclude=exclude)

        try:
            super().clean_fields(exclude=exclude)
        except ValidationError as e:
            errors = e.error_dict
        else:
            errors = {}

        self.validate_all_fields(errors=errors, exclude=exclude)

    def clean_all_fields(self, exclude=None):
        pass

    def validate_all_fields(self, errors, exclude=None):
        for field_name, validators in self.validators.items():
            f = self._meta.get_field(field_name)
            if (field_name in exclude):
                pass
            else:
                raw_value = getattr(self, f.attname)
                if ((f.blank) and (raw_value in f.empty_values)):
                    pass
                else:
                    try:
                        for validator in validators:
                            if (isinstance(validator, str)):
                                getattr(self, validator)()
                            else:
                                validator(raw_value)
                    except ValidationError as e:
                        errors[f.name] = [e.error_list[0].messages[0]]
        if (errors):
            raise ValidationError(errors)


class Entity(CleanAndValidateAllFieldsMixin, TimeStampedModel):
    id = SmallUDIDField()
    username = models.CharField(verbose_name=_('username'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    slug = models.CharField(verbose_name=_('username (slug)'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    photo = PhotoField(verbose_name=_('photo'), blank=True, null=True)
    special_username = models.BooleanField(verbose_name=_('Special username'), default=False)

    objects = EntityManager()

    @classproperty
    def settings(cls):
        return django_settings.ENTITY_SETTINGS

    @classproperty
    def validators(cls):
        validators = {
            'username': speedy_core_accounts_validators.get_username_validators(min_username_length=cls.settings.MIN_USERNAME_LENGTH, max_username_length=cls.settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=True),
            'slug': speedy_core_accounts_validators.get_slug_validators(min_username_length=cls.settings.MIN_USERNAME_LENGTH, max_username_length=cls.settings.MAX_USERNAME_LENGTH, min_slug_length=cls.settings.MIN_SLUG_LENGTH, max_slug_length=cls.settings.MAX_SLUG_LENGTH, allow_letters_after_digits=True) + ["validate_slug"],
        }
        return validators

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entities')
        ordering = ('-date_created',)

    def __str__(self):
        return '<Entity {} - {}>'.format(self.id, self.slug)
        # return '<Entity {} - username={}, slug={}>'.format(self.id, self.username, self.slug)

    def clean_all_fields(self, exclude=None):
        super().clean_all_fields(exclude=exclude)

        self.normalize_slug_and_username()

    def normalize_slug_and_username(self):
        self.slug = normalize_slug(slug=self.slug)
        if (self.username):
            self.username = normalize_username(username=self.username)
        else:
            self.username = normalize_username(username=self.slug)

    def validate_slug(self):
        self.validate_username_for_slug()
        self.validate_username_required()
        self.validate_username_unique()

    def validate_username_for_slug(self):
        if (not (normalize_username(username=self.slug) == self.username)):
            raise ValidationError(_('Slug does not parse to username.'))

    def validate_username_required(self):
        if (not (len(self.username) > 0)):
            raise ValidationError(_('Username is required.'))

    def validate_username_unique(self):
        username_exists = Entity.objects.filter(username=self.username).exclude(pk=self.pk).exists()
        if (username_exists):
            raise ValidationError(self._meta.get_field('slug').error_messages['unique'])


class NamedEntity(Entity):
    name = models.CharField(verbose_name=_('name'), max_length=255)

    @classproperty
    def settings(cls):
        return django_settings.NAMED_ENTITY_SETTINGS

    class Meta:
        abstract = True

    def __str__(self):
        return '<NamedEntity {} - {}/{}>'.format(self.id, self.name, self.slug)
        # return '<NamedEntity {} - name={}, username={}, slug={}>'.format(self.id, self.name, self.username, self.slug)


class ReservedUsername(Entity):
    description = models.TextField(verbose_name=_('description'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)], blank=True)
    objects = BaseManager()

    class Meta:
        ordering = ('-date_created',)

    def __init__(self, *args, **kwargs):
        if (('username' in kwargs) and (not ('slug' in kwargs))):
            kwargs['slug'] = kwargs['username']
        super().__init__(*args, **kwargs)

    def __str__(self):
        return '<Reserved username {} - {}>'.format(self.id, self.username)
        # return '<Reserved username {} - username={}>'.format(self.id, self.username)

    def clean_fields(self, exclude=None):
        # ~~~~ TODO: fix models! Exceptions should be 'slug' or 'username' and not '__all__'.
        self.normalize_slug_and_username()
        self.validate_username_for_slug()
        self.validate_username_required()
        self.validate_username_unique()

        if (exclude is None):
            exclude = []

        # Reserved username can be less than 6 characters, and any alphanumeric sequence.
        exclude += ['username', 'slug']

        return super().clean_fields(exclude=exclude)


class User(PermissionsMixin, Entity, AbstractBaseUser):
    LOCALIZABLE_FIELDS = ('first_name', 'last_name', 'city')
    NAME_LOCALIZABLE_FIELDS = LOCALIZABLE_FIELDS[:2]
    NAME_REQUIRED_LOCALIZABLE_FIELDS = NAME_LOCALIZABLE_FIELDS[:1]

    GENDER_UNKNOWN = 0
    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDER_OTHER = 3
    GENDER_MAX_VALUE_PLUS_ONE = 4

    GENDER_FEMALE_STRING = 'female'
    GENDER_MALE_STRING = 'male'
    GENDER_OTHER_STRING = 'other'

    GENDER_CHOICES = (
        (GENDER_FEMALE, _("Female")),
        (GENDER_MALE, _("Male")),
        (GENDER_OTHER, _("Other")),
    )
    GENDER_VALID_VALUES = [choice[0] for choice in GENDER_CHOICES]
    GENDERS_DICT = {GENDER_FEMALE: GENDER_FEMALE_STRING, GENDER_MALE: GENDER_MALE_STRING, GENDER_OTHER: GENDER_OTHER_STRING}

    DIET_UNKNOWN = 0
    DIET_VEGAN = 1
    DIET_VEGETARIAN = 2
    DIET_CARNIST = 3
    DIET_MAX_VALUE_PLUS_ONE = 4

    DIET_CHOICES_WITH_DEFAULT = (
        (DIET_UNKNOWN, _("Unknown")),
        (DIET_VEGAN, _("Vegan (eats only plants and fungi)")),
        (DIET_VEGETARIAN, _("Vegetarian (doesn't eat fish and meat)")),
        (DIET_CARNIST, _("Carnist (eats animals)")),
    )
    DIET_VALID_CHOICES = DIET_CHOICES_WITH_DEFAULT[1:]
    DIET_VALID_VALUES = [choice[0] for choice in DIET_VALID_CHOICES]

    SMOKING_STATUS_UNKNOWN = 0
    SMOKING_STATUS_NOT_SMOKING = 1
    SMOKING_STATUS_SMOKING_OCCASIONALLY = 2
    SMOKING_STATUS_SMOKING = 3
    SMOKING_STATUS_MAX_VALUE_PLUS_ONE = 4

    SMOKING_STATUS_CHOICES_WITH_DEFAULT = (
        (SMOKING_STATUS_UNKNOWN, _("Unknown")),
        (SMOKING_STATUS_NOT_SMOKING, _("Not smoking")),
        (SMOKING_STATUS_SMOKING_OCCASIONALLY, _("Smoking occasionally")),
        (SMOKING_STATUS_SMOKING, _("Smoking")),
    )
    SMOKING_STATUS_VALID_CHOICES = SMOKING_STATUS_CHOICES_WITH_DEFAULT[1:]
    SMOKING_STATUS_VALID_VALUES = [choice[0] for choice in SMOKING_STATUS_VALID_CHOICES]

    RELATIONSHIP_STATUS_UNKNOWN = 0
    RELATIONSHIP_STATUS_SINGLE = 1
    RELATIONSHIP_STATUS_DIVORCED = 2
    RELATIONSHIP_STATUS_WIDOWED = 3
    RELATIONSHIP_STATUS_IN_RELATIONSHIP = 4
    RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP = 5
    RELATIONSHIP_STATUS_COMPLICATED = 6
    RELATIONSHIP_STATUS_SEPARATED = 7
    RELATIONSHIP_STATUS_ENGAGED = 8
    RELATIONSHIP_STATUS_MARRIED = 9
    RELATIONSHIP_STATUS_MAX_VALUE_PLUS_ONE = 10

    RELATIONSHIP_STATUS_CHOICES_WITH_DEFAULT = (
        (RELATIONSHIP_STATUS_UNKNOWN, _("Unknown")),
        (RELATIONSHIP_STATUS_SINGLE, _("Single")),
        (RELATIONSHIP_STATUS_DIVORCED, _("Divorced")),
        (RELATIONSHIP_STATUS_WIDOWED, _("Widowed")),
        (RELATIONSHIP_STATUS_IN_RELATIONSHIP, _("In a relationship")),
        (RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP, _("In an open relationship")),
        (RELATIONSHIP_STATUS_COMPLICATED, _("It's complicated")),
        (RELATIONSHIP_STATUS_SEPARATED, _("Separated")),
        (RELATIONSHIP_STATUS_ENGAGED, _("Engaged")),
        (RELATIONSHIP_STATUS_MARRIED, _("Married")),
    )
    RELATIONSHIP_STATUS_VALID_CHOICES = RELATIONSHIP_STATUS_CHOICES_WITH_DEFAULT[1:]
    RELATIONSHIP_STATUS_VALID_VALUES = [choice[0] for choice in RELATIONSHIP_STATUS_VALID_CHOICES]

    NOTIFICATIONS_OFF = 0
    NOTIFICATIONS_ON = 1

    NOTIFICATIONS_CHOICES = (
        (NOTIFICATIONS_ON, _("Notify me")),
        (NOTIFICATIONS_OFF, _("Don't notify me")),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth', 'gender', 'diet', 'slug']

    @staticmethod
    def diet_choices_with_description(gender):
        return (
            (__class__.DIET_VEGAN, pgettext_lazy(context=gender, message="Vegan (eats only plants and fungi)")),
            (__class__.DIET_VEGETARIAN, pgettext_lazy(context=gender, message="Vegetarian (doesn't eat fish and meat)")),
            (__class__.DIET_CARNIST, pgettext_lazy(context=gender, message="Carnist (eats animals)")),
        )

    @staticmethod
    def diet_choices(gender):
        return (
            (__class__.DIET_VEGAN, pgettext_lazy(context=gender, message="Vegan")),
            (__class__.DIET_VEGETARIAN, pgettext_lazy(context=gender, message="Vegetarian")),
            (__class__.DIET_CARNIST, pgettext_lazy(context=gender, message="Carnist")),
        )

    @staticmethod
    def smoking_status_choices(gender):
        return (
            (__class__.SMOKING_STATUS_NOT_SMOKING, pgettext_lazy(context=gender, message="Not smoking")),
            (__class__.SMOKING_STATUS_SMOKING_OCCASIONALLY, pgettext_lazy(context=gender, message="Smoking occasionally")),
            (__class__.SMOKING_STATUS_SMOKING, pgettext_lazy(context=gender, message="Smoking")),
        )

    @staticmethod
    def relationship_status_choices(gender):
        return (
            (__class__.RELATIONSHIP_STATUS_SINGLE, pgettext_lazy(context=gender, message="Single")),
            (__class__.RELATIONSHIP_STATUS_DIVORCED, pgettext_lazy(context=gender, message="Divorced")),
            (__class__.RELATIONSHIP_STATUS_WIDOWED, pgettext_lazy(context=gender, message="Widowed")),
            (__class__.RELATIONSHIP_STATUS_IN_RELATIONSHIP, pgettext_lazy(context=gender, message="In a relationship")),
            (__class__.RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP, pgettext_lazy(context=gender, message="In an open relationship")),
            (__class__.RELATIONSHIP_STATUS_COMPLICATED, pgettext_lazy(context=gender, message="It's complicated")),
            (__class__.RELATIONSHIP_STATUS_SEPARATED, pgettext_lazy(context=gender, message="Separated")),
            (__class__.RELATIONSHIP_STATUS_ENGAGED, pgettext_lazy(context=gender, message="Engaged")),
            (__class__.RELATIONSHIP_STATUS_MARRIED, pgettext_lazy(context=gender, message="Married")),
        )

    first_name = TranslatedField(
        field=models.CharField(verbose_name=_('first name'), max_length=150, default=None),
    )
    last_name = TranslatedField(
        field=models.CharField(verbose_name=_('last name'), max_length=150, blank=True, default=None),
    )
    gender = models.SmallIntegerField(verbose_name=_('I am'), choices=GENDER_CHOICES)
    date_of_birth = models.DateField(verbose_name=_('date of birth'))
    diet = models.SmallIntegerField(verbose_name=_('diet'), choices=DIET_CHOICES_WITH_DEFAULT, default=DIET_UNKNOWN)
    smoking_status = models.SmallIntegerField(verbose_name=_('smoking status'), choices=SMOKING_STATUS_CHOICES_WITH_DEFAULT, default=SMOKING_STATUS_UNKNOWN)
    relationship_status = models.SmallIntegerField(verbose_name=_('relationship status'), choices=RELATIONSHIP_STATUS_CHOICES_WITH_DEFAULT, default=RELATIONSHIP_STATUS_UNKNOWN)
    city = TranslatedField(
        field=models.CharField(verbose_name=_('Where do I live?'), max_length=120, blank=True, null=True),
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    has_confirmed_email = models.BooleanField(default=False)
    access_dob_day_month = UserAccessField(verbose_name=_('Who can view my birth month and day'), default=UserAccessField.ACCESS_ME)
    access_dob_year = UserAccessField(verbose_name=_('Who can view my birth year'), default=UserAccessField.ACCESS_ME)
    notify_on_message = models.SmallIntegerField(verbose_name=_('On new messages'), choices=NOTIFICATIONS_CHOICES, default=NOTIFICATIONS_ON)

    objects = UserManager()

    @classproperty
    def settings(cls):
        return django_settings.USER_SETTINGS

    @classproperty
    def AGE_VALID_VALUES_IN_MODEL(cls):
        return range(cls.settings.MIN_AGE_ALLOWED_IN_MODEL, cls.settings.MAX_AGE_ALLOWED_IN_MODEL)

    @classproperty
    def AGE_VALID_VALUES_IN_FORMS(cls):
        return range(cls.settings.MIN_AGE_ALLOWED_IN_FORMS, cls.settings.MAX_AGE_ALLOWED_IN_FORMS)

    @classproperty
    def validators(cls):
        validators = {
            'username': speedy_core_accounts_validators.get_username_validators(min_username_length=cls.settings.MIN_USERNAME_LENGTH, max_username_length=cls.settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=False),
            'slug': speedy_core_accounts_validators.get_slug_validators(min_username_length=cls.settings.MIN_USERNAME_LENGTH, max_username_length=cls.settings.MAX_USERNAME_LENGTH, min_slug_length=cls.settings.MIN_SLUG_LENGTH, max_slug_length=cls.settings.MAX_SLUG_LENGTH, allow_letters_after_digits=False) + ["validate_slug"],
            'date_of_birth': [speedy_core_accounts_validators.validate_date_of_birth_in_model],
            **{to_attribute(name='first_name', language_code=language_code): [speedy_core_accounts_validators.validate_first_name_in_model] for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='last_name', language_code=language_code): [speedy_core_accounts_validators.validate_last_name_in_model] for language_code, language_name in django_settings.LANGUAGES},
        }
        return validators

    @cached_property
    def name(self):
        return self.profile.get_name()

    @cached_property
    def full_name(self):
        return self.get_full_name()

    @cached_property
    def short_name(self):
        return self.get_short_name()

    @cached_property
    def email(self):
        emails = self.email_addresses.filter(is_primary=True)
        if (len(emails) == 1):
            return emails[0].email
        else:
            return None

    @cached_property
    def profile(self):
        if (not (hasattr(self, '_profile'))):
            self.refresh_all_profiles()
        return self._profile

    @cached_property
    def speedy_net_profile(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_speedy_net_profile'))):
                self.refresh_all_profiles()
            return self._speedy_net_profile

    @cached_property
    def speedy_match_profile(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_speedy_match_profile'))):
                self.refresh_all_profiles()
            return self._speedy_match_profile

    @cached_property
    def received_friendship_requests(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_received_friendship_requests'))):
                self._received_friendship_requests = self.get_received_friendship_requests()
            return self._received_friendship_requests

    @cached_property
    def received_friendship_requests_count(self):
        return len(self.received_friendship_requests)

    @cached_property
    def sent_friendship_requests(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_sent_friendship_requests'))):
                self._sent_friendship_requests = self.get_sent_friendship_requests()
            return self._sent_friendship_requests

    @cached_property
    def sent_friendship_requests_count(self):
        return len(self.sent_friendship_requests)

    @cached_property
    def all_friends(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_friends'))):
                self._friends = self.get_friends()
            return self._friends

    @cached_property
    def friends_count(self):
        return len(self.all_friends)

    @cached_property
    def all_speedy_net_friends(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_speedy_net_friends'))):
                self._speedy_net_friends = self.get_speedy_net_friends()
            return self._speedy_net_friends

    @cached_property
    def speedy_net_friends_count(self):
        return len(self.all_speedy_net_friends)

    @cached_property
    def friends_trans(self):
        if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            return pgettext_lazy(context=self.speedy_match_profile.get_match_gender(), message='Friends')
        else:
            return _('Friends')

    @cached_property
    def has_confirmed_email_or_registered_now(self):
        return ((self.has_confirmed_email) or (self.date_created > now() - timedelta(hours=2)))

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-speedy_net_site_profile__last_visit',)
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        # Depends on site: full name in Speedy Net, first name in Speedy Match.
        return '<User {} - {}/{}>'.format(self.id, self.name, self.slug)
        # return '<User {} - name={}, username={}, slug={}>'.format(self.id, self.name, self.username, self.slug)

    def _update_has_confirmed_email_field(self):
        speedy_net_site = Site.objects.get(pk=django_settings.SPEEDY_NET_SITE_ID)
        previous_has_confirmed_email = self.has_confirmed_email
        self.has_confirmed_email = (self.email_addresses.filter(is_confirmed=True).count() > 0)
        self.save_user_and_profile()
        if (not (self.has_confirmed_email == previous_has_confirmed_email)):
            logger.info('User::_update_has_confirmed_email_field::User {user} has_confirmed_email is {has_confirmed_email} on {site_name} (registered {registered_days_ago} days ago).'.format(
                site_name=_(speedy_net_site.name),
                user=self,
                has_confirmed_email=self.has_confirmed_email,
                registered_days_ago=(now() - self.date_created).days,
            ))

    def save(self, *args, **kwargs):
        # Superuser must be equal to staff.
        if (not (self.is_superuser == self.is_staff)):
            raise ValidationError(_("Superuser must be equal to staff."))
        return super().save(*args, **kwargs)

    def set_password(self, raw_password):
        password_validation.validate_password(password=raw_password)
        return super().set_password(raw_password=raw_password)

    def delete(self, *args, **kwargs):
        if ((self.is_staff) or (self.is_superuser)):
            warnings.warn('Can’t delete staff user.')
            return False
        else:
            with transaction.atomic():
                for user_email_address in self.email_addresses.all():
                    user_email_address.delete()
                return_value = super().delete(*args, **kwargs)
            return return_value

    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        if (exclude is None):
            exclude = []

        # If special username is true, don't validate username.
        if (self.special_username):
            # ~~~~ TODO: fix models! Exceptions should be 'slug' and not '__all__'.
            self.normalize_slug_and_username()
            self.validate_username_for_slug()
            self.validate_username_required()
            self.validate_username_unique()
            exclude += ['username', 'slug']

        return super().clean_fields(exclude=exclude)

    def clean_all_fields(self, exclude=None):
        super().clean_all_fields(exclude=exclude)

        for base_field_name in __class__.NAME_LOCALIZABLE_FIELDS:
            self.clean_localizable_field(base_field_name=base_field_name)

    def clean_localizable_field(self, base_field_name):
        field_names = get_all_field_names(base_field_name=base_field_name)
        for field_name in field_names:
            if (not (string_is_not_none(getattr(self, field_name)))):
                for _field_name in field_names:
                    # Check again because maybe this field changed.
                    if (not (string_is_not_none(getattr(self, field_name)))):
                        if (string_is_not_none(getattr(self, _field_name))):
                            setattr(self, field_name, getattr(self, _field_name))

    def get_absolute_url(self):
        return reverse('profiles:user', kwargs={'slug': self.slug})

    def mail_user(self, template_name_prefix, context=None, send_to_unconfirmed=False):
        site = Site.objects.get_current()
        context = context or {}
        addresses = self.email_addresses.filter(is_primary=True)
        if (not (send_to_unconfirmed)):
            addresses = addresses.filter(is_confirmed=True)
        addresses = list(addresses)
        context.update({
            'site_name': _(site.name),
            'user': self,
        })
        if (addresses):
            return addresses[0].mail(template_name_prefix=template_name_prefix, context=context)
        return False

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name).strip() or self.slug

    def get_first_name(self):
        return '{}'.format(self.first_name).strip() or self.slug

    def get_short_name(self):
        return self.get_first_name()

    def activate(self):
        self.is_active = True
        self.save_user_and_profile()

    def get_profile(self, model=None, profile_model=None) -> 'SiteProfileBase':
        if (model is None):
            model = get_site_profile_model(profile_model=profile_model)
        profile = getattr(self, model.RELATED_NAME, None)
        if (profile is None):
            profile = model.objects.get_or_create(user=self)[0]
        return profile

    def refresh_all_profiles(self):
        self._profile = self.get_profile()
        if (django_settings.LOGIN_ENABLED):
            from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
            self._speedy_net_profile = self.get_profile(model=SpeedyNetSiteProfile)
            self._speedy_match_profile = self.get_profile(model=SpeedyMatchSiteProfile)

    def get_received_friendship_requests(self):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        logger.debug("User::get_received_friendship_requests:start:user={self}".format(
            self=self,
        ))
        SiteProfile = get_site_profile_model()
        qs = self.friendship_requests_received.all().prefetch_related("from_user", "from_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "from_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'from_user__photo').distinct().order_by('-from_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))
        received_friendship_requests = [friendship_request for friendship_request in qs if (friendship_request.from_user.profile.is_active)]
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            logger.debug("User::get_received_friendship_requests:SPEEDY_NET:end:user={self}, number_of_received_friendship_requests={number_of_received_friendship_requests}".format(
                self=self,
                number_of_received_friendship_requests=len(received_friendship_requests),
            ))
            return received_friendship_requests
        elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            from_list = [friendship_request.from_user_id for friendship_request in received_friendship_requests]
            matches_list = SpeedyMatchSiteProfile.objects.get_matches_from_list(user=self, from_list=from_list)
            received_friendship_requests = [friendship_request for friendship_request in received_friendship_requests if (friendship_request.from_user in matches_list)]
            logger.debug("User::get_received_friendship_requests:SPEEDY_MATCH:end:user={self}, number_of_received_friendship_requests={number_of_received_friendship_requests}".format(
                self=self,
                number_of_received_friendship_requests=len(received_friendship_requests),
            ))
            return received_friendship_requests
        else:
            raise NotImplementedError()

    def get_sent_friendship_requests(self):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        logger.debug("User::get_sent_friendship_requests:start:user={self}".format(
            self=self,
        ))
        SiteProfile = get_site_profile_model()
        qs = self.friendship_requests_sent.all().prefetch_related("to_user", "to_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "to_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'to_user__photo').distinct().order_by('-to_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))
        sent_friendship_requests = [friendship_request for friendship_request in qs if (friendship_request.to_user.profile.is_active)]
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            logger.debug("User::get_sent_friendship_requests:SPEEDY_NET:end:user={self}, number_of_sent_friendship_requests={number_of_sent_friendship_requests}".format(
                self=self,
                number_of_sent_friendship_requests=len(sent_friendship_requests),
            ))
            return sent_friendship_requests
        elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            from_list = [friendship_request.to_user_id for friendship_request in sent_friendship_requests]
            matches_list = SpeedyMatchSiteProfile.objects.get_matches_from_list(user=self, from_list=from_list)
            sent_friendship_requests = [friendship_request for friendship_request in sent_friendship_requests if (friendship_request.to_user in matches_list)]
            logger.debug("User::get_sent_friendship_requests:SPEEDY_MATCH:end:user={self}, number_of_sent_friendship_requests={number_of_sent_friendship_requests}".format(
                self=self,
                number_of_sent_friendship_requests=len(sent_friendship_requests),
            ))
            return sent_friendship_requests
        else:
            raise NotImplementedError()

    def get_speedy_net_friends(self):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        logger.debug("User::get_speedy_net_friends:start:user={self}".format(
            self=self,
        ))
        SiteProfile = get_site_profile_model()
        qs = self.friends.all().prefetch_related("from_user", "from_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "from_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'from_user__photo').distinct().order_by('-from_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))
        friends = [friendship for friendship in qs if (friendship.from_user.speedy_net_profile.is_active)]
        logger.debug("User::get_speedy_net_friends:end:user={self}, number_of_friends={number_of_friends}".format(
            self=self,
            number_of_friends=len(friends),
        ))
        return friends

    def get_friends(self):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        logger.debug("User::get_friends:start:user={self}".format(
            self=self,
        ))
        SiteProfile = get_site_profile_model()
        qs = self.friends.all().prefetch_related("from_user", "from_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "from_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'from_user__photo').distinct().order_by('-from_user__{}__last_visit'.format(SiteProfile.RELATED_NAME))
        friends = [friendship for friendship in qs if (friendship.from_user.profile.is_active)]
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            logger.debug("User::get_friends:SPEEDY_NET:end:user={self}, number_of_friends={number_of_friends}".format(
                self=self,
                number_of_friends=len(friends),
            ))
            return friends
        elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            from_list = [friendship.from_user_id for friendship in friends]
            matches_list = SpeedyMatchSiteProfile.objects.get_matches_from_list(user=self, from_list=from_list)
            friends = [friendship for friendship in friends if (friendship.from_user in matches_list)]
            logger.debug("User::get_friends:SPEEDY_MATCH:end:user={self}, number_of_friends={number_of_friends}".format(
                self=self,
                number_of_friends=len(friends),
            ))
            return friends
        else:
            raise NotImplementedError()

    def save_user_and_profile(self):
        with transaction.atomic():
            self.save()
            self.profile.save()
            if (django_settings.LOGIN_ENABLED):
                self.speedy_net_profile.save()
                self.speedy_match_profile.save()

    def get_gender(self):
        return self.__class__.GENDERS_DICT.get(self.gender)

    def get_diet(self):
        diets = {
            self.__class__.DIET_VEGAN: pgettext_lazy(context=self.get_gender(), message="Vegan"),
            self.__class__.DIET_VEGETARIAN: pgettext_lazy(context=self.get_gender(), message="Vegetarian"),
            self.__class__.DIET_CARNIST: pgettext_lazy(context=self.get_gender(), message="Carnist"),
        }
        return diets.get(self.diet, "")

    def get_smoking_status(self):
        smoking_statuses = {
            self.__class__.SMOKING_STATUS_NOT_SMOKING: pgettext_lazy(context=self.get_gender(), message="Not smoking"),
            self.__class__.SMOKING_STATUS_SMOKING_OCCASIONALLY: pgettext_lazy(context=self.get_gender(), message="Smoking occasionally"),
            self.__class__.SMOKING_STATUS_SMOKING: pgettext_lazy(context=self.get_gender(), message="Smoking"),
        }
        return smoking_statuses.get(self.smoking_status, "")

    def get_relationship_status(self):
        relationship_statuses = {
            self.__class__.RELATIONSHIP_STATUS_SINGLE: pgettext_lazy(context=self.get_gender(), message="Single"),
            self.__class__.RELATIONSHIP_STATUS_DIVORCED: pgettext_lazy(context=self.get_gender(), message="Divorced"),
            self.__class__.RELATIONSHIP_STATUS_WIDOWED: pgettext_lazy(context=self.get_gender(), message="Widowed"),
            self.__class__.RELATIONSHIP_STATUS_IN_RELATIONSHIP: pgettext_lazy(context=self.get_gender(), message="In a relationship"),
            self.__class__.RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP: pgettext_lazy(context=self.get_gender(), message="In an open relationship"),
            self.__class__.RELATIONSHIP_STATUS_COMPLICATED: pgettext_lazy(context=self.get_gender(), message="It's complicated"),
            self.__class__.RELATIONSHIP_STATUS_SEPARATED: pgettext_lazy(context=self.get_gender(), message="Separated"),
            self.__class__.RELATIONSHIP_STATUS_ENGAGED: pgettext_lazy(context=self.get_gender(), message="Engaged"),
            self.__class__.RELATIONSHIP_STATUS_MARRIED: pgettext_lazy(context=self.get_gender(), message="Married"),
        }
        return relationship_statuses.get(self.relationship_status, "")

    def get_age(self):
        return get_age(date_of_birth=self.date_of_birth)

    def get_diet_choices_with_description(self):
        return self.__class__.diet_choices_with_description(gender=self.get_gender())

    def get_smoking_status_choices(self):
        return self.__class__.smoking_status_choices(gender=self.get_gender())

    def get_relationship_status_choices(self):
        return self.__class__.relationship_status_choices(gender=self.get_gender())


User.ALL_GENDERS = [User.GENDERS_DICT[gender] for gender in User.GENDER_VALID_VALUES]  # ~~~~ TODO: maybe rename to ALL_GENDERS_STRINGS?


class UserEmailAddress(CleanAndValidateAllFieldsMixin, TimeStampedModel):
    id = RegularUDIDField()
    user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE, related_name='email_addresses')
    email = models.EmailField(verbose_name=_('email'), unique=True)
    is_confirmed = models.BooleanField(verbose_name=_('is confirmed'), default=False)
    is_primary = models.BooleanField(verbose_name=_('is primary'), default=False)
    confirmation_token = models.CharField(verbose_name=_('confirmation token'), max_length=32, blank=True)
    confirmation_sent = models.IntegerField(verbose_name=_('confirmation sent'), default=0)
    access = UserAccessField(verbose_name=_('Who can see this email'), default=UserAccessField.ACCESS_ME)

    @classproperty
    def validators(cls):
        validators = {
            'email': ["validate_email"],
        }
        return validators

    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')
        ordering = ('date_created',)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if (not (self.confirmation_token)):
            self.confirmation_token = self._generate_confirmation_token()
        return super().save(*args, **kwargs)

    def clean_all_fields(self, exclude=None):
        super().clean_all_fields(exclude=exclude)

        self.normalize_email()

    def normalize_email(self):
        self.email = normalize_email(email=self.email)

    def validate_email(self):
        self.validate_email_unique()

    def validate_email_unique(self):
        speedy_core_accounts_validators.validate_email_unique(email=self.email, user_email_address_pk=self.pk)

    def _generate_confirmation_token(self):
        return generate_confirmation_token()

    def mail(self, template_name_prefix, context=None):
        site = Site.objects.get_current()
        context = context or {}
        context.update({
            'site_name': _(site.name),
            'user': self.user,
            'email_address': self,
        })
        return send_mail(to=[self.email], template_name_prefix=template_name_prefix, context=context)

    def send_confirmation_email(self):
        if (self.user.has_confirmed_email):
            msg_count = self.mail(template_name_prefix='email/accounts/confirm_second_email')
        else:
            msg_count = self.mail(template_name_prefix='email/accounts/confirm_first_email')
        self.confirmation_sent += 1
        self.save(update_fields={'confirmation_sent'})
        return msg_count

    def verify(self):
        self.is_confirmed = True
        self.save(update_fields={'is_confirmed'})
        if (UserEmailAddress.objects.filter(user=self.user, is_confirmed=True).count() == 1):
            # If this user doesn't have a confirmed primary email address, make this one primary.
            if (UserEmailAddress.objects.filter(user=self.user, is_primary=True, is_confirmed=True).count() == 0):
                self.make_primary()
            self.user.profile.call_after_verify_email_address()

    def make_primary(self):
        self.user.email_addresses.update(is_primary=False)
        self.is_primary = True
        self.save(update_fields={'is_primary'})


class SiteProfileBase(TimeStampedModel):
    """
    SiteProfile contains site-specific user django_settings.
    """
    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name='+')
    last_visit = models.DateTimeField(_('last visit'), auto_now_add=True)
    is_active = True

    @cached_property
    def is_active_and_valid(self):
        raise NotImplementedError("is_active_and_valid is not implemented.")

    class Meta:
        abstract = True

    def __str__(self):
        return '<User Profile {} - {}/{}>'.format(self.user.id, self.user.name, self.user.slug)
        # return '<User Profile {} - name={}, username={}, slug={}>'.format(self.user.id, self.user.name, self.user.username, self.user.slug)

    def save(self, *args, **kwargs):
        return_value = super().save(*args, **kwargs)
        self.user.refresh_all_profiles()
        return return_value

    def update_last_visit(self):
        self.last_visit = now()
        self.user.save_user_and_profile()

    def activate(self):
        raise NotImplementedError("activate is not implemented.")

    def deactivate(self):
        raise NotImplementedError("deactivate is not implemented.")

    def get_name(self):
        raise NotImplementedError("get_name is not implemented.")

    def validate_profile_and_activate(self):
        raise NotImplementedError("validate_profile_and_activate is not implemented.")

    def call_after_verify_email_address(self):
        raise NotImplementedError("call_after_verify_email_address is not implemented.")


@receiver(signal=models.signals.post_save, sender=UserEmailAddress)
def update_user_has_confirmed_email_field_after_saving_email_address(sender, instance: UserEmailAddress, **kwargs):
    instance.user._update_has_confirmed_email_field()
    # If the user doesn't have a primary email address, and this is the only email - make this email primary.
    if ((instance.user.email_addresses.filter(is_primary=True).count() == 0) and (instance.user.email_addresses.count() == 1)):
        instance.make_primary()


@receiver(signal=models.signals.post_delete, sender=UserEmailAddress)
def update_user_has_confirmed_email_field_after_deleting_email_address(sender, instance: UserEmailAddress, **kwargs):
    instance.user._update_has_confirmed_email_field()


