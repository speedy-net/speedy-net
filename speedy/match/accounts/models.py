import logging

from django.db import models
from django.conf import settings as django_settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import gettext_lazy as _, pgettext_lazy, get_language
from django.core.exceptions import ValidationError

from translated_fields import TranslatedField

from speedy.core.accounts.models import SiteProfileBase, User
from speedy.core.blocks.models import Block

from .managers import SiteProfileManager

logger = logging.getLogger(__name__)


class SiteProfile(SiteProfileBase):
    settings = django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS

    LOCALIZABLE_FIELDS = ('profile_description', 'city', 'children', 'more_children', 'match_description')

    RELATED_NAME = 'speedy_match_site_profile'

    HEIGHT_VALID_VALUES = range(settings.MIN_HEIGHT_ALLOWED, settings.MAX_HEIGHT_ALLOWED + 1)
    AGE_MATCH_VALID_VALUES = range(settings.MIN_AGE_MATCH_ALLOWED, settings.MAX_AGE_MATCH_ALLOWED + 1)

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
        (MARITAL_STATUS_IN_RELATIONSHIP, _("In a relatioship")),
        (MARITAL_STATUS_IN_OPEN_RELATIONSHIP, _("In an open relationship")),
        (MARITAL_STATUS_COMPLICATED, _("It's complicated")),
        (MARITAL_STATUS_SEPARATED, _("Separated")),
        (MARITAL_STATUS_MARRIED, _("Married")),
    )
    MARITAL_STATUS_VALID_CHOICES = MARITAL_STATUS_CHOICES_WITH_DEFAULT[1:]
    MARITAL_STATUS_VALID_VALUES = [choice[0] for choice in MARITAL_STATUS_VALID_CHOICES]

    RANK_0 = 0
    RANK_1 = 1
    RANK_2 = 2
    RANK_3 = 3
    RANK_4 = 4
    RANK_5 = 5

    RANK_CHOICES = (
        (RANK_0, _("0 hearts")),
        (RANK_1, _("1 hearts")),
        (RANK_2, _("2 hearts")),
        (RANK_3, _("3 hearts")),
        (RANK_4, _("4 hearts")),
        (RANK_5, _("5 hearts")),
    )
    RANK_VALID_VALUES = [choice[0] for choice in RANK_CHOICES]

    @staticmethod
    def gender_to_match_default():
        return list()

    @staticmethod
    def diet_match_default():
        return dict({str(diet): __class__.RANK_5 for diet in User.DIET_VALID_VALUES})

    @staticmethod
    def smoking_status_match_default():
        return dict({str(smoking_status): __class__.RANK_5 for smoking_status in __class__.SMOKING_STATUS_VALID_VALUES})

    @staticmethod
    def marital_status_match_default():
        return dict({str(marital_status): __class__.RANK_5 for marital_status in __class__.MARITAL_STATUS_VALID_VALUES})

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
            (__class__.MARITAL_STATUS_IN_RELATIONSHIP, pgettext_lazy(context=gender, message="In a relatioship")),
            (__class__.MARITAL_STATUS_IN_OPEN_RELATIONSHIP, pgettext_lazy(context=gender, message="In an open relationship")),
            (__class__.MARITAL_STATUS_COMPLICATED, pgettext_lazy(context=gender, message="It's complicated")),
            (__class__.MARITAL_STATUS_SEPARATED, pgettext_lazy(context=gender, message="Separated")),
            (__class__.MARITAL_STATUS_MARRIED, pgettext_lazy(context=gender, message="Married")),
        )

    user = models.OneToOneField(to=User, verbose_name=_('user'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    notify_on_like = models.PositiveIntegerField(verbose_name=_('on new likes'), choices=User.NOTIFICATIONS_CHOICES, default=User.NOTIFICATIONS_ON)
    active_languages = models.TextField(verbose_name=_('active languages'), blank=True)
    height = models.SmallIntegerField(verbose_name=_('height'), help_text=_('cm'), blank=True, null=True)
    # ~~~~ TODO: diet, smoking_status and marital_status - decide which model should contain them - are they relevant also to Speedy Net or only to Speedy Match?
    smoking_status = models.SmallIntegerField(verbose_name=_('smoking status'), choices=SMOKING_STATUS_CHOICES_WITH_DEFAULT, default=SMOKING_STATUS_UNKNOWN)
    marital_status = models.SmallIntegerField(verbose_name=_('marital status'), choices=MARITAL_STATUS_CHOICES_WITH_DEFAULT, default=MARITAL_STATUS_UNKNOWN)
    profile_description = TranslatedField(
        models.TextField(verbose_name=_('Few words about me'), blank=True, null=True)
    )
    city = TranslatedField(
        models.CharField(verbose_name=_('city or locality'), max_length=255, blank=True, null=True)
    )
    children = TranslatedField(
        models.TextField(verbose_name=_('Do you have children? How many?'), blank=True, null=True)
    )
    more_children = TranslatedField(
        models.TextField(verbose_name=_('Do you want (more) children?'), blank=True, null=True)
    )
    match_description = TranslatedField(
        models.TextField(verbose_name=_('My ideal match'), blank=True, null=True)
    )
    gender_to_match = ArrayField(models.SmallIntegerField(), verbose_name=_('Gender'), size=len(User.GENDER_VALID_VALUES), default=gender_to_match_default.__func__, blank=True, null=True)
    min_age_match = models.SmallIntegerField(verbose_name=_('minimal age to match'), default=settings.MIN_AGE_MATCH_ALLOWED)
    max_age_match = models.SmallIntegerField(verbose_name=_('maximal age to match'), default=settings.MAX_AGE_MATCH_ALLOWED)
    diet_match = JSONField(verbose_name=_('diet match'), default=diet_match_default.__func__)
    smoking_status_match = JSONField(verbose_name=_('smoking status match'), default=smoking_status_match_default.__func__)
    marital_status_match = JSONField(verbose_name=_('marital status match'), default=marital_status_match_default.__func__)
    activation_step = models.PositiveSmallIntegerField(default=2)

    objects = SiteProfileManager()

    @property
    def is_active(self):
        return ((self.user.is_active) and (get_language() in self.get_active_languages()))

    class Meta:
        verbose_name = _('Speedy Match Profile')
        verbose_name_plural = _('Speedy Match Profiles')

    def __str__(self):
        return '{} @ Speedy Match'.format(self.user)

    def _set_active_languages(self, languages):
        languages = sorted(list(set(languages)))
        self.active_languages = ','.join(set(languages))

    def _deactivate_language(self, step):
        # Profile is invalid. Deactivate in this language.
        language_code = get_language()
        self._set_active_languages(set(self.get_active_languages()) - {language_code})
        self.activation_step = step
        self.user.save_user_and_profile()

    def get_active_languages(self):
        return list(filter(None, (l.strip() for l in self.active_languages.split(','))))

    def validate_profile_and_activate(self):
        # ~~~~ TODO: all the error messages in this function may depend on the current user's (or other user's) gender.
        from speedy.match.accounts import utils
        language_code = get_language()
        error_messages = []
        for step in utils.get_steps_range():
            fields = utils.get_step_fields_to_validate(step=step)
            for field_name in fields:
                try:
                    utils.validate_field(field_name=field_name, user=self.user)
                except ValidationError as e:
                    error_messages.append(str(e))
            if (len(error_messages) > 0):
                self._deactivate_language(step=step)
                return step, error_messages
        # Registration form is complete. Check if the user has a confirmed email address.
        step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
        if ((self.user.has_confirmed_email()) and (step >= self.activation_step)):
            # Profile is valid. Activate in this language.
            languages = self.get_active_languages()
            if (not (language_code in languages)):
                languages.append(language_code)
                self._set_active_languages(languages=languages)
                self.user.save_user_and_profile()
        else:
            self._deactivate_language(step=self.activation_step)
            error_messages.append(_("Please confirm your email address."))
        return step, error_messages

    def call_after_verify_email_address(self):
        old_step = self.activation_step
        self.activation_step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
        self.validate_profile_and_activate()
        self.activation_step = old_step
        self.user.save_user_and_profile()

    def get_matching_rank(self, other_profile, second_call=True) -> int:
        self.validate_profile_and_activate()
        try:
            other_profile.validate_profile_and_activate()
        except ValidationError as e:
            logger.error("get_matching_rank::other_profile.validate_profile_and_activate() failed, other_profile.user.pk={other_user_pk}, other_profile.user.username={other_user_username}, other_profile.user.slug={other_user_slug}, e={e}".format(
                other_user_pk=other_profile.user.pk,
                other_user_username=other_profile.user.username,
                other_user_slug=other_profile.user.slug,
                e=e,
            ))
            return self.__class__.RANK_0
        if (self.user.pk == other_profile.user.pk):
            return self.__class__.RANK_0
        if ((self.is_active) and (other_profile.is_active)):
            if (Block.objects.there_is_block(user_1=self.user, user_2=other_profile.user)):
                return self.__class__.RANK_0
            if (other_profile.user.gender not in self.gender_to_match):
                return self.__class__.RANK_0
            if (not (self.min_age_match <= other_profile.user.get_age() <= self.max_age_match)):
                return self.__class__.RANK_0
            if (other_profile.user.diet == User.DIET_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.smoking_status == self.__class__.SMOKING_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.marital_status == self.__class__.MARITAL_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            diet_rank = self.diet_match.get(str(other_profile.user.diet), self.__class__.RANK_5)
            smoking_status_rank = self.smoking_status_match.get(str(other_profile.smoking_status), self.__class__.RANK_5)
            marital_status_rank = self.marital_status_match.get(str(other_profile.marital_status), self.__class__.RANK_5)
            rank = min([diet_rank, smoking_status_rank, marital_status_rank])
            if (rank > self.__class__.RANK_0) and (second_call):
                other_user_rank = other_profile.get_matching_rank(other_profile=self, second_call=False)
                if (other_user_rank == self.__class__.RANK_0):
                    rank = self.__class__.RANK_0
            other_profile.rank = rank
            return rank
        else:
            return self.__class__.RANK_0

    def deactivate(self):
        self._set_active_languages([])
        self.activation_step = 0
        self.user.save_user_and_profile()

    def get_name(self):
        # Speedy Match name is user's first name.
        return self.user.get_first_name()

    def get_match_gender(self):
        if (len(self.gender_to_match) == 1):
            return User.GENDERS_DICT.get(self.gender_to_match[0])
        else:
            return User.GENDERS_DICT.get(User.GENDER_OTHER)

    def get_smoking_status_choices(self):
        return self.__class__.smoking_status_choices(gender=self.user.get_gender())

    def get_marital_status_choices(self):
        return self.__class__.marital_status_choices(gender=self.user.get_gender())

    def get_diet_match_choices(self):
        return User.diet_choices(gender=self.get_match_gender())

    def get_smoking_status_match_choices(self):
        return self.__class__.smoking_status_choices(gender=self.get_match_gender())

    def get_marital_status_match_choices(self):
        return self.__class__.marital_status_choices(gender=self.get_match_gender())


