import logging

from django.conf import settings as django_settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from django.utils.functional import classproperty, cached_property
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

from translated_fields import TranslatedField

from speedy.core.base.utils import to_attribute
from speedy.core.accounts.cache_helper import bust_cache
from speedy.core.accounts.models import SiteProfileBase, User
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike
from .managers import SiteProfileManager

logger = logging.getLogger(__name__)


class SiteProfile(SiteProfileBase):
    LOCALIZABLE_FIELDS = ('profile_description', 'children', 'more_children', 'match_description')

    RELATED_NAME = 'speedy_match_site_profile'

    DELETED_NAME = _('Speedy Match User')

    RANK_0 = 0
    RANK_1 = 1
    RANK_2 = 2
    RANK_3 = 3
    RANK_4 = 4
    RANK_5 = 5

    RANK_CHOICES = (
        (RANK_0, _("No match")),
        (RANK_1, _("One heart")),
        (RANK_2, _("Two hearts")),
        (RANK_3, _("Three hearts")),
        (RANK_4, _("Four hearts")),
        (RANK_5, _("Five hearts")),
    )
    RANK_VALID_VALUES = [choice[0] for choice in RANK_CHOICES]

    @staticmethod
    def active_languages_default():
        return list()

    @staticmethod
    def gender_to_match_default():
        return list()

    @staticmethod
    def min_age_to_match_default():
        return __class__.settings.MIN_AGE_TO_MATCH_ALLOWED

    @staticmethod
    def max_age_to_match_default():
        return __class__.settings.MAX_AGE_TO_MATCH_ALLOWED

    @staticmethod
    def diet_match_default():
        return dict({str(diet): __class__.RANK_5 for diet in User.DIET_VALID_VALUES})

    @staticmethod
    def smoking_status_match_default():
        return dict({str(smoking_status): __class__.RANK_5 for smoking_status in User.SMOKING_STATUS_VALID_VALUES})

    @staticmethod
    def relationship_status_match_default():
        return dict({str(relationship_status): __class__.RANK_5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES})

    @staticmethod
    def diet_to_match_default():
        return list()

    @staticmethod
    def smoking_status_to_match_default():
        return list()

    @staticmethod
    def relationship_status_to_match_default():
        return list()

    @staticmethod
    def get_rank_description(rank):
        rank_descriptions = {
            __class__.RANK_0: _("No match"),
            __class__.RANK_1: _("One heart"),
            __class__.RANK_2: _("Two hearts"),
            __class__.RANK_3: _("Three hearts"),
            __class__.RANK_4: _("Four hearts"),
            __class__.RANK_5: _("Five hearts"),
        }
        return rank_descriptions.get(rank, "")

    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    notify_on_like = models.SmallIntegerField(verbose_name=_('On new likes'), choices=User.NOTIFICATIONS_CHOICES, default=User.NOTIFICATIONS_ON)
    active_languages = ArrayField(
        base_field=models.CharField(max_length=2, choices=django_settings.LANGUAGES),
        verbose_name=_('Active languages'),
        size=len(django_settings.LANGUAGES),
        default=active_languages_default.__func__,
        blank=True,
        null=True,
    )
    height = models.SmallIntegerField(verbose_name=_('Height'), help_text=_('cm'), blank=True, null=True)
    profile_description = TranslatedField(
        field=models.TextField(verbose_name=_('Few words about me'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)], blank=True, null=True),
    )
    children = TranslatedField(
        field=models.TextField(verbose_name=_('Do you have children? How many?'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)], blank=True, null=True),
    )
    more_children = TranslatedField(
        field=models.TextField(verbose_name=_('Do you want (more) children?'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)], blank=True, null=True),
    )
    match_description = TranslatedField(
        field=models.TextField(verbose_name=_('My ideal match'), max_length=50000, validators=[MaxLengthValidator(limit_value=50000)], blank=True, null=True),
    )
    gender_to_match = ArrayField(
        base_field=models.SmallIntegerField(choices=User.GENDER_CHOICES),
        verbose_name=_('Gender to match'),
        size=len(User.GENDER_VALID_VALUES),
        default=gender_to_match_default.__func__,
        blank=True,
        null=True,
    )
    min_age_to_match = models.SmallIntegerField(verbose_name=_('Minimal age to match'), default=min_age_to_match_default.__func__)
    max_age_to_match = models.SmallIntegerField(verbose_name=_('Maximal age to match'), default=max_age_to_match_default.__func__)
    diet_match = models.JSONField(verbose_name=_('Diet match'), default=diet_match_default.__func__)
    smoking_status_match = models.JSONField(verbose_name=_('Smoking status match'), default=smoking_status_match_default.__func__)
    relationship_status_match = models.JSONField(verbose_name=_('Relationship status match'), default=relationship_status_match_default.__func__)
    diet_to_match = ArrayField(
        base_field=models.SmallIntegerField(choices=User.DIET_VALID_CHOICES),
        verbose_name=_('Diet to match'),
        size=len(User.DIET_VALID_VALUES),
        default=diet_to_match_default.__func__,
        blank=True,
        null=True,
    )
    smoking_status_to_match = ArrayField(
        base_field=models.SmallIntegerField(choices=User.SMOKING_STATUS_VALID_CHOICES),
        verbose_name=_('Smoking status to match'),
        size=len(User.SMOKING_STATUS_VALID_VALUES),
        default=smoking_status_to_match_default.__func__,
        blank=True,
        null=True,
    )
    relationship_status_to_match = ArrayField(
        base_field=models.SmallIntegerField(choices=User.RELATIONSHIP_STATUS_VALID_CHOICES),
        verbose_name=_('Relationship status to match'),
        size=len(User.RELATIONSHIP_STATUS_VALID_VALUES),
        default=relationship_status_to_match_default.__func__,
        blank=True,
        null=True,
    )
    activation_step = TranslatedField(
        field=models.PositiveSmallIntegerField(verbose_name=_('Activation step'), default=2),
    )
    number_of_matches = TranslatedField(
        field=models.PositiveSmallIntegerField(verbose_name=_("Number of matches on last user's search"), default=None, blank=True, null=True),
    )
    profile_picture_months_offset = models.PositiveSmallIntegerField(default=5)  # If a face is detected, will be 0. Otherwise, will be 5 months.
    not_allowed_to_use_speedy_match = models.BooleanField(default=False)  # If set to True, user will have no matches.
    likes_to_user_count = models.PositiveIntegerField(default=0)

    objects = SiteProfileManager()

    @classproperty
    def settings(cls):
        return django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS

    @classproperty
    def HEIGHT_VALID_VALUES(cls):
        return range(cls.settings.MIN_HEIGHT_ALLOWED, cls.settings.MAX_HEIGHT_ALLOWED + 1)

    @classproperty
    def AGE_TO_MATCH_VALID_VALUES(cls):
        return range(cls.settings.MIN_AGE_TO_MATCH_ALLOWED, cls.settings.MAX_AGE_TO_MATCH_ALLOWED + 1)

    @cached_property
    def is_active(self):
        return ((self.user.is_active) and (get_language() in self.active_languages))

    @cached_property
    def is_active_and_valid(self):
        if (self.is_active):
            step, error_messages = self.validate_profile_and_activate(commit=False)
            error = False
            if (len(error_messages) > 0):
                error = True
            if (not (step == len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
                error = True
            if (error):
                logger.error("is_active_and_valid::user is active but not valid, step={step}, error_messages={error_messages}, self.user.pk={self_user_pk}, self.user.username={self_user_username}, self.user.slug={self_user_slug} (registered {registered_days_ago} days ago)".format(
                    step=step,
                    error_messages=error_messages,
                    self_user_pk=self.user.pk,
                    self_user_username=self.user.username,
                    self_user_slug=self.user.slug,
                    registered_days_ago=(now() - self.user.date_created).days,
                ))
                return False
        return (self.is_active)

    class Meta:
        verbose_name = _('Speedy Match Profile')
        verbose_name_plural = _('Speedy Match Profiles')
        ordering = ('-last_visit', 'user_id')

    def __str__(self):
        return '{} @ Speedy Match'.format(super().__str__())

    def _get_deleted_name(self):
        return self.__class__.DELETED_NAME

    def _set_values_to_match(self):
        from speedy.match.accounts import utils
        self._set_active_languages(languages=self.active_languages)
        self.gender_to_match = sorted(list(set(self.gender_to_match)))
        errors = 0
        for field_name in ['diet_match', 'smoking_status_match', 'relationship_status_match']:
            try:
                utils.validate_field(field_name=field_name, user=self.user)
            except (ValidationError, AttributeError):
                errors += 1
        if (errors == 0):
            self.diet_to_match = [diet for diet in User.DIET_VALID_VALUES if (self.diet_match[str(diet)] > self.__class__.RANK_0)]
            self.smoking_status_to_match = [smoking_status for smoking_status in User.SMOKING_STATUS_VALID_VALUES if (self.smoking_status_match[str(smoking_status)] > self.__class__.RANK_0)]
            self.relationship_status_to_match = [relationship_status for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES if (self.relationship_status_match[str(relationship_status)] > self.__class__.RANK_0)]
        else:
            self.diet_to_match = list()
            self.smoking_status_to_match = list()
            self.relationship_status_to_match = list()

    def _set_active_languages(self, languages):
        self.active_languages = sorted(list(set(languages)))
        if ("is_active" in self.__dict__):
            del self.is_active
        if ("is_active_and_valid" in self.__dict__):
            del self.is_active_and_valid

    def _deactivate_language(self, step, commit=True):
        # Profile is invalid. Deactivate in this language.
        language_code = get_language()
        self._set_active_languages(languages=set(self.active_languages) - {language_code})
        self.activation_step = step
        if (commit):
            self.user.save_user_and_profile()

    def _get_matching_rank(self, other_profile, second_call=True) -> int:
        """
        Get the matching rank between self and other_profile.

        :param self:
        :param other_profile:
        :param second_call:
        :return: The matching rank between self and other_profile.
        """
        self._get_matching_rank_calls = getattr(self, "_get_matching_rank_calls", 0) + 1
        if (self._get_matching_rank_calls >= 5):
            logger.debug('_get_matching_rank::_get_matching_rank_calls={_get_matching_rank_calls}, self={self}, other_profile={other_profile}'.format(_get_matching_rank_calls=self._get_matching_rank_calls, self=self, other_profile=other_profile))
        if (self.user.pk == other_profile.user.pk):
            return self.__class__.RANK_0
        if ((self.is_active_and_valid) and (other_profile.is_active_and_valid)):
            if (Block.objects.there_is_block(entity_1=self.user, entity_2=other_profile.user)):
                return self.__class__.RANK_0
            if (not ((__class__.settings.MIN_HEIGHT_TO_MATCH <= self.height <= __class__.settings.MAX_HEIGHT_TO_MATCH) and (__class__.settings.MIN_HEIGHT_TO_MATCH <= other_profile.height <= __class__.settings.MAX_HEIGHT_TO_MATCH))):
                return self.__class__.RANK_0
            if (self.not_allowed_to_use_speedy_match or other_profile.not_allowed_to_use_speedy_match):
                return self.__class__.RANK_0
            if (other_profile.user.gender not in self.gender_to_match):
                return self.__class__.RANK_0
            if (not (self.min_age_to_match <= other_profile.user.get_age() <= self.max_age_to_match)):
                return self.__class__.RANK_0
            if (other_profile.user.diet == User.DIET_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.user.smoking_status == User.SMOKING_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.user.relationship_status == User.RELATIONSHIP_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            diet_rank = self.diet_match.get(str(other_profile.user.diet), self.__class__.RANK_0)
            smoking_status_rank = self.smoking_status_match.get(str(other_profile.user.smoking_status), self.__class__.RANK_0)
            relationship_status_rank = self.relationship_status_match.get(str(other_profile.user.relationship_status), self.__class__.RANK_0)
            rank = min([diet_rank, smoking_status_rank, relationship_status_rank])
            if (rank > self.__class__.RANK_0) and (second_call):
                other_user_rank = other_profile._get_matching_rank(other_profile=self, second_call=False)
                if (other_user_rank == self.__class__.RANK_0):
                    rank = self.__class__.RANK_0
            return rank
        else:
            if (self.is_active):
                if (not (self.is_active_and_valid)):
                    logger.error('_get_matching_rank::get inside "if (not (self.is_active_and_valid)):", self={self}, other_profile={other_profile}'.format(self=self, other_profile=other_profile))
            if (other_profile.is_active):
                if (not (other_profile.is_active_and_valid)):
                    logger.error('_get_matching_rank::get inside "if (not (other_profile.is_active_and_valid)):", self={self}, other_profile={other_profile}'.format(self=self, other_profile=other_profile))
            return self.__class__.RANK_0

    def save(self, *args, **kwargs):
        if (hasattr(self, "_rank_dict")):
            delattr(self, "_rank_dict")
        self._set_values_to_match()
        if (self.activation_step < 2):
            self.activation_step = 2
        if (self.activation_step > len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)):
            self.activation_step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
        if ((self.is_active) and (self.activation_step < len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
            self._deactivate_language(step=self.activation_step, commit=False)
        if ((len(self.active_languages) > 0) and (not (self.user.has_confirmed_email))):
            self._set_active_languages(languages=[])
        if ((len(self.active_languages) > 0) and (self.not_allowed_to_use_speedy_match)):
            self._set_active_languages(languages=[])
        return super().save(*args, **kwargs)

    def validate_profile_and_activate(self, commit=True):
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
                if (commit):
                    self._deactivate_language(step=step)
                return step, error_messages
        # Check if the user is not allowed to use Speedy Match.
        if (self.not_allowed_to_use_speedy_match):
            step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS) - 1
            return step, error_messages
        # Registration form is complete. Check if the user has a confirmed email address.
        step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
        if ((self.user.has_confirmed_email) and (step >= self.activation_step)):
            if (commit):
                # Profile is valid. Activate in this language.
                self.activation_step = step
                languages = self.active_languages
                if (not (language_code in languages)):
                    languages.append(language_code)
                    self._set_active_languages(languages=languages)
                self.user.save_user_and_profile()
        else:
            if (commit):
                self._deactivate_language(step=self.activation_step)
            error_messages.append(_("Please confirm your email address."))
        return step, error_messages

    def call_after_verify_email_address(self):
        pass

    def get_matching_rank(self, other_profile) -> int:
        """
        Get the matching rank between self and other_profile.

        :param self:
        :param other_profile:
        :return: The matching rank between self and other_profile.
        """
        if (self.user.pk == other_profile.user.pk):
            return self.__class__.RANK_0
        rank_dict = getattr(self, "_rank_dict", {})
        if (other_profile.user.pk in rank_dict):
            rank = rank_dict[other_profile.user.pk]
        else:
            rank = self._get_matching_rank(other_profile=other_profile)
            rank_dict[other_profile.user.pk] = rank
            self._rank_dict = rank_dict
        other_profile.rank = rank
        self.rank = self.__class__.RANK_0
        return rank

    def deactivate(self):
        self._set_active_languages(languages=[])
        self.activation_step = 2
        for language_code, language_name in django_settings.LANGUAGES:
            setattr(self, to_attribute(name='activation_step', language_code=language_code), 2)
        self.user.save_user_and_profile()

    def get_name(self):
        if (self.user.is_deleted):
            return self._get_deleted_name()
        # Speedy Match name is the user's first name.
        return self.user.get_first_name()

    def get_match_gender(self):
        if (len(self.gender_to_match) == 1):
            match_gender = User.GENDERS_DICT.get(self.gender_to_match[0])
        else:
            match_gender = User.GENDERS_DICT.get(User.GENDER_OTHER)
        return match_gender

    def get_like_gender(self):
        """
        If there is only one gender to match, and at least 90% of the liked and liking users genders are equal to this gender, return this gender.

        Otherwise, return "other".

        (Actually 100% of the liked and liking users genders should be equal to this gender if there was always only one gender to match for this user, but some users change their gender, and therefore we allow up to 10% of the users to change their genders and not to be equal to this gender.)

        We don't query the database of liked and liking users if len(self.gender_to_match) is not 1.
        """
        like_gender = None
        if (len(self.gender_to_match) == 1):
            match_gender = self.get_match_gender()
            like_users_genders_1 = [like.to_user.get_gender() for like in UserLike.objects.filter(from_user=self.user).prefetch_related("to_user").distinct()] + [like.from_user.get_gender() for like in UserLike.objects.filter(to_user=self.user).prefetch_related("from_user").distinct()]
            like_users_genders_2 = [gender for gender in like_users_genders_1 if (gender == match_gender)]
            if (len(like_users_genders_2) >= 0.9 * len(like_users_genders_1)):
                like_gender = match_gender
        if (like_gender is None):
            like_gender = User.GENDERS_DICT.get(User.GENDER_OTHER)
        return like_gender

    def get_diet_match_choices(self):
        return User.diet_choices(gender=self.get_match_gender())

    def get_smoking_status_match_choices(self):
        return User.smoking_status_choices(gender=self.get_match_gender())

    def get_relationship_status_match_choices(self):
        return User.relationship_status_choices(gender=self.get_match_gender())


@receiver(signal=models.signals.post_save, sender=SiteProfile)
def invalidate_matches_after_update_site_profile(sender, instance: SiteProfile, **kwargs):
    if (not (getattr(instance, '_in_update_last_visit', None))):
        bust_cache(cache_type='matches', entities_pks=[instance.user.pk])


