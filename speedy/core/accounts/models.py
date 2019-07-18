import logging
import warnings
from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models, transaction
from django.utils.timezone import now
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from translated_fields import TranslatedField

# from speedy.net.settings import global_settings as speedy_net_global_settings # ~~~~ TODO: should be in django_settings? # ~~~~ TODO: remove this line!
from speedy.core.base.mail import send_mail
from speedy.core.base.models import TimeStampedModel, SmallUDIDField, RegularUDIDField
from speedy.core.base.utils import normalize_slug, normalize_username, generate_confirmation_token, get_age, string_is_not_empty, get_all_field_names
from speedy.core.uploads.fields import PhotoField
from .managers import EntityManager, UserManager
from .utils import get_site_profile_model, normalize_email
from .validators import get_username_validators, get_slug_validators, validate_date_of_birth_in_model, validate_email_unique

logger = logging.getLogger(__name__)


class CleanAndValidateAllFieldsMixin(object):
    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        if exclude is None:
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
    settings = django_settings.ENTITY_SETTINGS
    # settings = speedy_net_global_settings.EntitySettings # ~~~~ TODO: remove this line!

    id = SmallUDIDField()
    username = models.CharField(verbose_name=_('username'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    slug = models.CharField(verbose_name=_('username (slug)'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    photo = PhotoField(verbose_name=_('photo'), blank=True, null=True)

    objects = EntityManager()

    @property
    def validators(self):
        validators = {
            'username': get_username_validators(min_username_length=self.settings.MIN_USERNAME_LENGTH, max_username_length=self.settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=True),
            'slug': get_slug_validators(min_username_length=self.settings.MIN_USERNAME_LENGTH, max_username_length=self.settings.MAX_USERNAME_LENGTH, min_slug_length=self.settings.MIN_SLUG_LENGTH, max_slug_length=self.settings.MAX_SLUG_LENGTH, allow_letters_after_digits=True) + ["validate_slug"],
        }
        return validators

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entities')
        ordering = ('id',)

    def __str__(self):
        return '<Entity {}>'.format(self.id)

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
        self.validate_username_unique()

    def validate_username_for_slug(self):
        if (not (normalize_username(username=self.slug) == self.username)):
            raise ValidationError(_('Slug does not parse to username.'))

    def validate_username_unique(self):
        username_exists = Entity.objects.filter(username=self.username).exclude(pk=self.pk).exists()
        if (username_exists):
            raise ValidationError(self._meta.get_field('slug').error_messages['unique'])


class NamedEntity(Entity):
    settings = django_settings.NAMED_ENTITY_SETTINGS
    # settings = speedy_net_global_settings.NamedEntitySettings # ~~~~ TODO: remove this line!

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

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'choices': self.ACCESS_CHOICES,
        })
        super().__init__(*args, **kwargs)


class User(PermissionsMixin, Entity, AbstractBaseUser):
    settings = django_settings.USER_SETTINGS
    # settings = speedy_net_global_settings.UserSettings # ~~~~ TODO: remove this line!

    LOCALIZABLE_FIELDS = ('first_name', 'last_name')

    AGE_VALID_VALUES_IN_MODEL = range(settings.MIN_AGE_ALLOWED_IN_MODEL, settings.MAX_AGE_ALLOWED_IN_MODEL)
    AGE_VALID_VALUES_IN_FORMS = range(settings.MIN_AGE_ALLOWED_IN_FORMS, settings.MAX_AGE_ALLOWED_IN_FORMS)

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
    # print(GENDERS_DICT) # for debugging. # ~~~~ TODO: remove this line!
    # ALL_GENDERS = [GENDERS_DICT[gender] for gender in GENDER_VALID_VALUES] # ~~~~ TODO: remove this line!
    # ALL_GENDERS = GENDERS_DICT # ~~~~ TODO: remove this line!
    # ALL_GENDERS = [__class__.GENDERS_DICT[gender] for gender in __class__.GENDER_VALID_VALUES] # ~~~~ TODO: maybe rename to ALL_GENDERS_STRINGS? # ~~~~ TODO: remove this line!
    # ALL_GENDERS = [__class__.GENDERS_DICT[gender] for gender in __class__.GENDER_VALID_VALUES] # ~~~~ TODO: maybe rename to ALL_GENDERS_STRINGS? # ~~~~ TODO: remove this line!

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
    SMOKING_STATUS_NO = 1
    SMOKING_STATUS_SOMETIMES = 2
    SMOKING_STATUS_YES = 3
    SMOKING_STATUS_MAX_VALUE_PLUS_ONE = 4

    SMOKING_STATUS_CHOICES_WITH_DEFAULT = (
        (SMOKING_STATUS_UNKNOWN, _("Unknown")),
        (SMOKING_STATUS_NO, _("No")),
        (SMOKING_STATUS_SOMETIMES, _("Sometimes")),
        (SMOKING_STATUS_YES, _("Yes")),
    )
    SMOKING_STATUS_VALID_CHOICES = SMOKING_STATUS_CHOICES_WITH_DEFAULT[1:]
    SMOKING_STATUS_VALID_VALUES = [choice[0] for choice in SMOKING_STATUS_VALID_CHOICES]

    MARITAL_STATUS_UNKNOWN = 0
    MARITAL_STATUS_SINGLE = 1
    MARITAL_STATUS_DIVORCED = 2
    MARITAL_STATUS_WIDOWED = 3
    MARITAL_STATUS_IN_RELATIONSHIP = 4
    MARITAL_STATUS_IN_OPEN_RELATIONSHIP = 5
    MARITAL_STATUS_COMPLICATED = 6
    MARITAL_STATUS_SEPARATED = 7
    MARITAL_STATUS_MARRIED = 8
    MARITAL_STATUS_MAX_VALUE_PLUS_ONE = 9

    MARITAL_STATUS_CHOICES_WITH_DEFAULT = (
        (MARITAL_STATUS_UNKNOWN, _("Unknown")),
        (MARITAL_STATUS_SINGLE, _("Single")),
        (MARITAL_STATUS_DIVORCED, _("Divorced")),
        (MARITAL_STATUS_WIDOWED, _("Widowed")),
        (MARITAL_STATUS_IN_RELATIONSHIP, _("In a relationship")),
        (MARITAL_STATUS_IN_OPEN_RELATIONSHIP, _("In an open relationship")),
        (MARITAL_STATUS_COMPLICATED, _("It's complicated")),
        (MARITAL_STATUS_SEPARATED, _("Separated")),
        (MARITAL_STATUS_MARRIED, _("Married")),
    )
    MARITAL_STATUS_VALID_CHOICES = MARITAL_STATUS_CHOICES_WITH_DEFAULT[1:]
    MARITAL_STATUS_VALID_VALUES = [choice[0] for choice in MARITAL_STATUS_VALID_CHOICES]

    NOTIFICATIONS_OFF = 0
    NOTIFICATIONS_ON = 1

    NOTIFICATIONS_CHOICES = (
        (NOTIFICATIONS_ON, _("Notify me")),
        (NOTIFICATIONS_OFF, _("Don't notify me")),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth', 'gender', 'diet', 'slug']

    @staticmethod
    def diet_choices(gender):
        return (
            # (__class__.DIET_UNKNOWN, _("Unknown")), # ~~~~ TODO: remove this line!
            (__class__.DIET_VEGAN, pgettext_lazy(context=gender, message="Vegan (eats only plants and fungi)")),
            (__class__.DIET_VEGETARIAN, pgettext_lazy(context=gender, message="Vegetarian (doesn't eat fish and meat)")),
            (__class__.DIET_CARNIST, pgettext_lazy(context=gender, message="Carnist (eats animals)")),
        )

    @staticmethod
    def smoking_status_choices(gender):
        return (
            # (__class__.SMOKING_STATUS_UNKNOWN, _("Unknown")), # ~~~~ TODO: remove this line!
            (__class__.SMOKING_STATUS_NO, pgettext_lazy(context=gender, message="No")),
            (__class__.SMOKING_STATUS_SOMETIMES, pgettext_lazy(context=gender, message="Sometimes")),
            (__class__.SMOKING_STATUS_YES, pgettext_lazy(context=gender, message="Yes")),
        )

    @staticmethod
    def marital_status_choices(gender):
        return (
            # (__class__.MARITAL_STATUS_UNKNOWN, _("Unknown")), # ~~~~ TODO: remove this line!
            (__class__.MARITAL_STATUS_SINGLE, pgettext_lazy(context=gender, message="Single")),
            (__class__.MARITAL_STATUS_DIVORCED, pgettext_lazy(context=gender, message="Divorced")),
            (__class__.MARITAL_STATUS_WIDOWED, pgettext_lazy(context=gender, message="Widowed")),
            (__class__.MARITAL_STATUS_IN_RELATIONSHIP, pgettext_lazy(context=gender, message="In a relationship")),
            (__class__.MARITAL_STATUS_IN_OPEN_RELATIONSHIP, pgettext_lazy(context=gender, message="In an open relationship")),
            (__class__.MARITAL_STATUS_COMPLICATED, pgettext_lazy(context=gender, message="It's complicated")),
            (__class__.MARITAL_STATUS_SEPARATED, pgettext_lazy(context=gender, message="Separated")),
            (__class__.MARITAL_STATUS_MARRIED, pgettext_lazy(context=gender, message="Married")),
        )

    first_name = TranslatedField(
        field=models.CharField(verbose_name=_('first name'), max_length=75),
    )
    last_name = TranslatedField(
        field=models.CharField(verbose_name=_('last name'), max_length=75),
    )
    gender = models.SmallIntegerField(verbose_name=_('I am'), choices=GENDER_CHOICES)
    date_of_birth = models.DateField(verbose_name=_('date of birth'))
    diet = models.SmallIntegerField(verbose_name=_('diet'), choices=DIET_CHOICES_WITH_DEFAULT, default=DIET_UNKNOWN)
    smoking_status = models.SmallIntegerField(verbose_name=_('smoking status'), choices=SMOKING_STATUS_CHOICES_WITH_DEFAULT, default=SMOKING_STATUS_UNKNOWN)
    marital_status = models.SmallIntegerField(verbose_name=_('marital status'), choices=MARITAL_STATUS_CHOICES_WITH_DEFAULT, default=MARITAL_STATUS_UNKNOWN)
    city = TranslatedField(
        field=models.CharField(verbose_name=_('city or locality'), max_length=120, blank=True, null=True),
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    access_dob_day_month = UserAccessField(verbose_name=_('who can view my birth month and day'), default=UserAccessField.ACCESS_ME)
    access_dob_year = UserAccessField(verbose_name=_('who can view my birth year'), default=UserAccessField.ACCESS_ME)
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=NOTIFICATIONS_CHOICES, default=NOTIFICATIONS_ON)

    objects = UserManager()

    @property
    def validators(self):
        validators = {
            'username': get_username_validators(min_username_length=self.settings.MIN_USERNAME_LENGTH, max_username_length=self.settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=False),
            'slug': get_slug_validators(min_username_length=self.settings.MIN_USERNAME_LENGTH, max_username_length=self.settings.MAX_USERNAME_LENGTH, min_slug_length=self.settings.MIN_SLUG_LENGTH, max_slug_length=self.settings.MAX_SLUG_LENGTH, allow_letters_after_digits=False) + ["validate_slug"],
            'date_of_birth': [validate_date_of_birth_in_model],
        }
        return validators

    @property
    def email(self):
        try:
            return self.email_addresses.get(is_primary=True).email
        except UserEmailAddress.DoesNotExist:
            return None

    @property
    def profile(self):
        if (not (hasattr(self, '_profile'))):
            self.refresh_all_profiles()
        return self._profile

    @property
    def speedy_net_profile(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_speedy_net_profile'))):
                self.refresh_all_profiles()
            return self._speedy_net_profile

    @property
    def speedy_match_profile(self):
        if (django_settings.LOGIN_ENABLED):
            if (not (hasattr(self, '_speedy_match_profile'))):
                self.refresh_all_profiles()
            return self._speedy_match_profile

    @property
    def all_received_friendship_requests(self):
        SiteProfile = get_site_profile_model()
        table_name = SiteProfile._meta.db_table
        extra_select = {
            'last_visit': 'SELECT last_visit FROM {} WHERE user_id = friendship_friendshiprequest.to_user_id'.format(table_name),
        }
        qs = self.user.friendship_requests_received.all().extra(select=extra_select).order_by('-last_visit')
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            return qs
        elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
            qs = [u for u in qs if (self.user.profile.get_matching_rank(other_profile=u.from_user.profile) > SpeedyMatchSiteProfile.RANK_0)]
            return qs
        else:
            raise NotImplementedError()

    @property
    def received_friendship_requests_count(self):
        return len(self.all_received_friendship_requests)

    @property
    def all_sent_friendship_requests(self):
        SiteProfile = get_site_profile_model()
        table_name = SiteProfile._meta.db_table
        extra_select = {
            'last_visit': 'SELECT last_visit FROM {} WHERE user_id = friendship_friendshiprequest.from_user_id'.format(table_name),
        }
        qs = self.user.friendship_requests_sent.all().extra(select=extra_select).order_by('-last_visit')
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            return qs
        elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
            qs = [u for u in qs if (self.user.profile.get_matching_rank(other_profile=u.to_user.profile) > SpeedyMatchSiteProfile.RANK_0)]
            return qs
        else:
            raise NotImplementedError()

    @property
    def sent_friendship_requests_count(self):
        return len(self.all_sent_friendship_requests)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-last_login', 'id')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        # Depends on site: full name in Speedy Net, first name in Speedy Match.
        return self.profile.get_name()

    def set_password(self, raw_password):
        password_validation.validate_password(password=raw_password)
        return super().set_password(raw_password=raw_password)

    def delete(self, *args, **kwargs):
        if ((self.is_staff) or (self.is_superuser)):
            warnings.warn('Can’t delete staff user.')
            return False
        else:
            return super().delete(*args, **kwargs)

    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        if exclude is None:
            exclude = []

        if (self.is_superuser):
            exclude = ['username', 'slug']

        return super().clean_fields(exclude=exclude)

    def clean_all_fields(self, exclude=None):
        super().clean_all_fields(exclude=exclude)

        for base_field_name in __class__.LOCALIZABLE_FIELDS:
            self.clean_localizable_field(base_field_name=base_field_name)

    def clean_localizable_field(self, base_field_name):
        # raise Exception(base_field_name)############ # ~~~~ TODO: remove this line!
        field_names = get_all_field_names(base_field_name=base_field_name)
        for field_name in field_names:
            if (not (string_is_not_empty(getattr(self, field_name)))):
                for _field_name in field_names:
                    # Check again because maybe this field is already not empty.
                    if (not (string_is_not_empty(getattr(self, field_name)))):
                        if (string_is_not_empty(getattr(self, _field_name))):
                            setattr(self, field_name, getattr(self, _field_name))

    def get_absolute_url(self):
        return reverse('profiles:user', kwargs={'slug': self.slug})

    def mail_user(self, template_name_prefix, context=None, send_to_unconfirmed=False):
        addresses = self.email_addresses.filter(is_primary=True)
        if (not (send_to_unconfirmed)):
            addresses = addresses.filter(is_confirmed=True)
        addresses = list(addresses)
        if (addresses):
            return addresses[0].mail(template_name_prefix=template_name_prefix, context=context)
        return False

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name).strip() or self.slug

    def get_first_name(self):
        return '{}'.format(self.first_name).strip() or self.slug

    def get_short_name(self):
        return self.get_first_name()

    def has_confirmed_email(self):
        return (self.email_addresses.filter(is_confirmed=True).exists())

    @cached_property
    def has_confirmed_email_or_registered_now(self):
        return ((self.has_confirmed_email()) or (self.date_created > now() - timedelta(hours=2)))

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

    def save_user_and_profile(self):
        with transaction.atomic():
            self.save()
            self.profile.save()
            if (django_settings.LOGIN_ENABLED):
                self.speedy_net_profile.save() # ~~~~ TODO: is this necessary?
                self.speedy_match_profile.save() # ~~~~ TODO: is this necessary?

    def get_gender(self):
        return self.__class__.GENDERS_DICT.get(self.gender)

    def get_diet(self):
        diets = {
            self.__class__.DIET_VEGAN: pgettext_lazy(context=self.get_gender(), message='Vegan'),
            self.__class__.DIET_VEGETARIAN: pgettext_lazy(context=self.get_gender(), message='Vegetarian'),
            self.__class__.DIET_CARNIST: pgettext_lazy(context=self.get_gender(), message='Carnist'),
        }
        return diets.get(self.diet)

    def get_age(self):
        return get_age(date_of_birth=self.date_of_birth)

    def get_diet_choices(self):
        return self.__class__.diet_choices(gender=self.get_gender())

    def get_smoking_status_choices(self):
        return self.__class__.smoking_status_choices(gender=self.user.get_gender())

    def get_marital_status_choices(self):
        return self.__class__.marital_status_choices(gender=self.user.get_gender())


User.ALL_GENDERS = [User.GENDERS_DICT[gender] for gender in User.GENDER_VALID_VALUES] # ~~~~ TODO: maybe rename to ALL_GENDERS_STRINGS?


class UserEmailAddress(CleanAndValidateAllFieldsMixin, TimeStampedModel):
    id = RegularUDIDField()
    user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE, related_name='email_addresses')
    email = models.EmailField(verbose_name=_('email'), unique=True)
    is_confirmed = models.BooleanField(verbose_name=_('is confirmed'), default=False)
    is_primary = models.BooleanField(verbose_name=_('is primary'), default=False)
    confirmation_token = models.CharField(verbose_name=_('confirmation token'), max_length=32, blank=True)
    confirmation_sent = models.IntegerField(verbose_name=_('confirmation sent'), default=0)
    access = UserAccessField(verbose_name=_('who can see this email'), default=UserAccessField.ACCESS_ME)

    @property
    def validators(self):
        validators = {
            'email': ["validate_email"],
        }
        return validators

    class Meta:
        verbose_name = _('email address')
        verbose_name_plural = _('email addresses')
        ordering = ('date_created', 'id',)

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
        validate_email_unique(email=self.email, user_email_address_pk=self.pk)

    def _generate_confirmation_token(self):
        return generate_confirmation_token()

    def mail(self, template_name_prefix, context=None):
        context = context or {}
        context.update({
            'email_address': self,
            'user': self.user,
        })
        return send_mail(to=[self.email], template_name_prefix=template_name_prefix, context=context)

    def send_confirmation_email(self):
        msg_count = self.mail('accounts/email/verify_email')
        self.confirmation_sent += 1
        self.save(update_fields={'confirmation_sent'})
        return msg_count

    def verify(self):
        self.is_confirmed = True
        self.save(update_fields={'is_confirmed'})
        if (UserEmailAddress.objects.filter(user=self.user, is_confirmed=True).count() == 1):
            self.user.profile.call_after_verify_email_address()

    def make_primary(self):
        self.user.email_addresses.update(is_primary=False)
        self.is_primary = True
        self.save(update_fields={'is_primary'})


class SiteProfileBase(TimeStampedModel):
    """
    SiteProfile contains site-specific user django_settings.
    """

    user = models.OneToOneField(to=User, verbose_name=_('user'), primary_key=True, on_delete=models.CASCADE, related_name='+')
    last_visit = models.DateTimeField(_('last visit'), auto_now_add=True)
    is_active = True

    @property
    def is_active_or_superuser(self):
        return self.is_active or self.user.is_superuser

    class Meta:
        abstract = True

    def __str__(self):
        return '{}'.format(self.user)

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


