import warnings
from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models, transaction
from django.utils.timezone import now
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from speedy.net.settings import global_settings as speedy_net_global_settings # ~~~~ TODO: should be in django_settings?
from speedy.core.base.mail import send_mail
from speedy.core.base.models import TimeStampedModel, SmallUDIDField, RegularUDIDField
from speedy.core.base.utils import normalize_slug, normalize_username, generate_confirmation_token, get_age
from speedy.core.uploads.fields import PhotoField
from .managers import EntityManager, UserManager
from .utils import get_site_profile_model
from .validators import get_username_validators, get_slug_validators, validate_date_of_birth_in_model, ValidateUserPasswordMixin
# from .mixins import CleanEmailMixin # ~~~~ TODO


class Entity(TimeStampedModel):
    settings = speedy_net_global_settings.EntitySettings

    id = SmallUDIDField()
    username = models.CharField(verbose_name=_('username'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    slug = models.CharField(verbose_name=_('username (slug)'), max_length=255, unique=True, error_messages={'unique': _('This username is already taken.')})
    photo = PhotoField(verbose_name=_('photo'), blank=True, null=True)

    validators = {
        'username': get_username_validators(min_username_length=settings.MIN_USERNAME_LENGTH, max_username_length=settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=True),
        'slug': get_slug_validators(min_username_length=settings.MIN_USERNAME_LENGTH, max_username_length=settings.MAX_USERNAME_LENGTH, min_slug_length=settings.MIN_SLUG_LENGTH, max_slug_length=settings.MAX_SLUG_LENGTH, allow_letters_after_digits=True),
    }

    objects = EntityManager()

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entities')
        ordering = ('id',)

    def __str__(self):
        return '<Entity {}>'.format(self.id)

    def normalize_slug_and_username(self):
        self.slug = normalize_slug(slug=self.slug)
        if (self.username):
            self.username = normalize_username(slug=self.username)
        else:
            self.username = normalize_username(slug=self.slug)

    def validate_username_for_slug(self):
        if (normalize_username(slug=self.slug) != self.username):
            raise ValidationError(_('Slug does not parse to username.'))

    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        self.normalize_slug_and_username()

        try:
            super().clean_fields(exclude=exclude)
        except ValidationError as e:
            errors = e.error_dict
        else:
            errors = {}

        username_exists = Entity.objects.filter(username=self.username).exclude(pk=self.pk).exists()
        if (username_exists):
            errors['slug'] = [self._meta.get_field('slug').error_messages['unique']]
            # errors['username'] = [self._meta.get_field('username').error_messages['unique']]

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
                            validator(raw_value)
                        if ((field_name == 'slug') and (self.username)):
                            self.validate_username_for_slug()
                    except ValidationError as e:
                        errors[f.name] = [e.error_list[0].messages[0]]
        if (errors):
            raise ValidationError(errors)


class NamedEntity(Entity):
    settings = speedy_net_global_settings.NamedEntitySettings

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


class User(ValidateUserPasswordMixin, PermissionsMixin, Entity, AbstractBaseUser):
    settings = speedy_net_global_settings.UserSettings

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

    first_name = models.CharField(verbose_name=_('first name'), max_length=75)
    last_name = models.CharField(verbose_name=_('last name'), max_length=75)
    gender = models.SmallIntegerField(verbose_name=_('I am'), choices=GENDER_CHOICES)
    # ~~~~ TODO - validate age between 0 and 250 in the model. Don't allow dates in the future or more than 250 years ago (including exactly 250 years).
    date_of_birth = models.DateField(verbose_name=_('date of birth'))
    # ~~~~ TODO: diet, smoking_status and marital_status - decide which model should contain them - are they relevant also to Speedy Net or only to Speedy Match?
    diet = models.SmallIntegerField(verbose_name=_('diet'), choices=DIET_CHOICES_WITH_DEFAULT, default=DIET_UNKNOWN)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    access_dob_day_month = UserAccessField(verbose_name=_('who can view my birth month and day'), default=UserAccessField.ACCESS_ME)
    access_dob_year = UserAccessField(verbose_name=_('who can view my birth year'), default=UserAccessField.ACCESS_ME)
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=NOTIFICATIONS_CHOICES, default=NOTIFICATIONS_ON)

    objects = UserManager()

    validators = {
        'username': get_username_validators(min_username_length=settings.MIN_USERNAME_LENGTH, max_username_length=settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=False),
        'slug': get_slug_validators(min_username_length=settings.MIN_USERNAME_LENGTH, max_username_length=settings.MAX_USERNAME_LENGTH, min_slug_length=settings.MIN_SLUG_LENGTH, max_slug_length=settings.MAX_SLUG_LENGTH, allow_letters_after_digits=False),
        'date_of_birth': [validate_date_of_birth_in_model],
    }

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-last_login', 'id')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        # Depends on site: full name in Speedy Net, first name in Speedy Match.
        return self.profile.get_name()

    def set_password(self, raw_password):
        self.validate_password(password=raw_password)
        return super().set_password(raw_password=raw_password)

    def delete(self, *args, **kwargs):
        if ((self.is_staff) or (self.is_superuser)):
            warnings.warn('Can’t delete staff user.')
            return False
        else:
            return super().delete(*args, **kwargs)

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
        return self.email_addresses.filter(is_confirmed=True).exists()

    @cached_property
    def has_verified_email(self):
        return self.has_confirmed_email() or self.date_created > now() - timedelta(hours=2)

    def activate(self):
        self.is_active = True
        self.save_user_and_profile()

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


User.ALL_GENDERS = [User.GENDERS_DICT[gender] for gender in User.GENDER_VALID_VALUES] # ~~~~ TODO: maybe rename to ALL_GENDERS_STRINGS?


# class UserEmailAddress(CleanEmailMixin, TimeStampedModel): # ~~~~ TODO
class UserEmailAddress(TimeStampedModel):
    id = RegularUDIDField()
    user = models.ForeignKey(to=django_settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE, related_name='email_addresses')
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
        if (not (self.confirmation_token)):
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
        return send_mail(to=[self.email], template_name_prefix=template_name_prefix, context=context)

    def send_confirmation_email(self):
        msg_count = self.mail('accounts/email/verify_email')
        self.confirmation_sent += 1
        self.save(update_fields={'confirmation_sent'})
        return msg_count

    def verify(self):
        self.is_confirmed = True
        self.save(update_fields={'is_confirmed'})
        if ((hasattr(self.user.profile, 'validate_profile_and_activate')) and (UserEmailAddress.objects.filter(user=self.user, is_confirmed=True).count() == 1)):
            old_step = self.user.profile.activation_step
            self.user.profile.activation_step = len(django_settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
            self.user.profile.validate_profile_and_activate()
            self.user.profile.activation_step = old_step
            self.user.profile.save(update_fields=['activation_step'])

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

    @property
    def is_active_or_superuser(self):
        return self.is_active or self.user.is_superuser


