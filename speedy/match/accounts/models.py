from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.exceptions import ValidationError

from speedy.core.accounts.models import SiteProfileBase, UserAccessField, User
from speedy.core.blocks.models import Block
from speedy.core.base.utils import get_age
from speedy.match.accounts import validators


class SiteProfile(SiteProfileBase):

    SMOKING_UNKNOWN = 0
    SMOKING_NO = 1
    SMOKING_SOMETIMES = 2
    SMOKING_YES = 3
    SMOKING_MAX_VALUE_PLUS_ONE = 4
    SMOKING_CHOICES = (
        (SMOKING_NO, _("No")),
        (SMOKING_SOMETIMES, _("Sometimes")),
        (SMOKING_YES, _("Yes")),
    )

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

    MARITAL_STATUS_CHOICES = (
        (MARITAL_STATUS_SINGLE, _("Single")),
        (MARITAL_STATUS_DIVORCED, _("Divorced")),
        (MARITAL_STATUS_WIDOWED, _("Widowed")),
        (MARITAL_STATUS_IN_RELATIONSHIP, _("In a relatioship")),
        (MARITAL_STATUS_IN_OPEN_RELATIONSHIP, _("In an open relationship")),
        (MARITAL_STATUS_COMPLICATED, _("It's complicated")),
        (MARITAL_STATUS_SEPARATED, _("Separated")),
        (MARITAL_STATUS_MARRIED, _("Married")),
    )

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

    notify_on_like = models.PositiveIntegerField(verbose_name=_('on new likes'), choices=User.NOTIFICATIONS_CHOICES, default=User.NOTIFICATIONS_ON)
    active_languages = models.TextField(verbose_name=_('active languages'), blank=True)

    height = models.SmallIntegerField(verbose_name=_('height'), help_text=_('cm'), null=True, validators=[validators.validate_height])
    min_age_match = models.SmallIntegerField(verbose_name=_('minimal age to match'), default=settings.MIN_AGE_ALLOWED, validators=[validators.validate_min_age_match])
    max_age_match = models.SmallIntegerField(verbose_name=_('maximal age to match'), default=settings.MAX_AGE_ALLOWED, validators=[validators.validate_max_age_match])
    smoking = models.SmallIntegerField(verbose_name=_('smoking status'), choices=SMOKING_CHOICES, default=SMOKING_UNKNOWN, validators=[validators.validate_smoking])
    city = models.CharField(verbose_name=_('city or locality'), max_length=255, null=True, validators=[validators.validate_city])
    marital_status = models.SmallIntegerField(verbose_name=_('marital status'), choices=MARITAL_STATUS_CHOICES, default=MARITAL_STATUS_UNKNOWN, validators=[validators.validate_marital_status])
    children = models.TextField(verbose_name=_('Do you have children? How many?'), null=True, validators=[validators.validate_children])
    more_children = models.TextField(verbose_name=_('Do you want (more) children?'), null=True, validators=[validators.validate_more_children])
    profile_description = models.TextField(verbose_name=_('Few words about me'), null=True, validators=[validators.validate_profile_description])
    match_description = models.TextField(verbose_name=_('My ideal match'), null=True, validators=[validators.validate_match_description])
    gender_to_match = ArrayField(models.SmallIntegerField(), verbose_name=_('Gender'), size=3, default=[], validators=[validators.validate_gender_to_match])

    diet_match = JSONField(verbose_name=('diet match'), default= {
        User.DIET_VEGAN: RANK_5,
        User.DIET_VEGETARIAN: RANK_5,
        User.DIET_CARNIST: RANK_5,
    }, validators=[validators.validate_diet_match])
    smoking_match = JSONField(verbose_name=('smoking status match'), default={
        SMOKING_NO: RANK_5,
        SMOKING_YES: RANK_5,
        SMOKING_SOMETIMES: RANK_5,
    }, validators=[validators.validate_smoking_match])
    marital_status_match = JSONField(verbose_name=_('marital status match'), default={
        MARITAL_STATUS_SINGLE: RANK_5,
        MARITAL_STATUS_DIVORCED: RANK_5,
        MARITAL_STATUS_WIDOWED: RANK_5,
        MARITAL_STATUS_IN_RELATIONSHIP: RANK_5,
        MARITAL_STATUS_IN_OPEN_RELATIONSHIP: RANK_5,
        MARITAL_STATUS_COMPLICATED: RANK_5,
        MARITAL_STATUS_SEPARATED: RANK_5,
        MARITAL_STATUS_MARRIED: RANK_5,
    }, validators=[validators.validate_marital_status_match])
    activation_step = models.PositiveSmallIntegerField(default=2)

    class Meta:
        verbose_name = 'Speedy Match Profile'
        verbose_name_plural = 'Speedy Match Profiles'

    def _set_active_languages(self, languages):
        languages = sorted(list(set(languages)))
        self.active_languages = ','.join(set(languages))

    def _deactivate_language(self, step):
        # Profile is invalid. Deactivate in this language.
        lang = get_language()
        self._set_active_languages(set(self.get_active_languages()) - {lang})
        self.activation_step = step
        self.save(update_fields={'active_languages', 'activation_step'})

    def get_active_languages(self):
        return list(filter(None, (l.strip() for l in self.active_languages.split(','))))

    def validate_profile_and_activate(self):
        # ~~~~ TODO: all the error messages in this function may depend on the current user's (or other user's) gender.
        lang = get_language()
        error_messages = []
        for step in range(1, len(settings.SITE_PROFILE_FORM_FIELDS) - 1):
            fields = settings.SITE_PROFILE_FORM_FIELDS[step]
            for field in fields:
                if field in ['photo']:
                    if (not (self.user.photo)):
                        try:
                            validators.validate_photo(photo=self.user.photo)
                        except ValidationError as e:
                            error_messages.append(str(e))
                elif field in ['profile_description']:
                    try:
                        validators.validate_profile_description(profile_description=self.profile_description)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['city']:
                    try:
                        validators.validate_city(city=self.city)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['children']:
                    try:
                        validators.validate_children(children=self.children)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['more_children']:
                    try:
                        validators.validate_more_children(more_children=self.more_children)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['match_description']:
                    try:
                        validators.validate_match_description(match_description=self.match_description)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['height']:
                    try:
                        validators.validate_height(height=self.height)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['diet']:
                    try:
                        validators.validate_diet(diet=self.user.diet)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['smoking']:
                    try:
                        validators.validate_smoking(smoking=self.smoking)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['marital_status']:
                    try:
                        validators.validate_marital_status(marital_status=self.marital_status)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['gender_to_match']:
                    try:
                        validators.validate_gender_to_match(gender_to_match=self.gender_to_match)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif field in ['min_age_match', 'max_age_match']:
                    if not (settings.MIN_AGE_ALLOWED <= self.min_age_match <= self.max_age_match <= settings.MAX_AGE_ALLOWED):
                        try:
                            validators.validate_min_age_match(min_age_match=self.min_age_match)
                        except ValidationError as e:
                            error_messages.append(str(e))
                        try:
                            validators.validate_max_age_match(max_age_match=self.max_age_match)
                        except ValidationError as e:
                            error_messages.append(str(e))
                        try:
                            validators.validate_min_max_age_to_match(min_age_match=self.min_age_match, max_age_match=self.max_age_match)
                        except ValidationError as e:
                            error_messages.append(str(e))
                elif (field in ['diet_match']):
                    try:
                        validators.validate_diet_match(diet_match=self.diet_match)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif (field in ['smoking_match']):
                    try:
                        validators.validate_smoking_match(smoking_match=self.smoking_match)
                    except ValidationError as e:
                        error_messages.append(str(e))
                elif (field in ['marital_status_match']):
                    try:
                        validators.validate_marital_status_match(marital_status_match=self.marital_status_match)
                    except ValidationError as e:
                        error_messages.append(str(e))
            if (len(error_messages) > 0):
                self._deactivate_language(step=step)
                return step, error_messages
        # Registration form is complete. Check if the user has a confirmed email address.
        step = len(settings.SITE_PROFILE_FORM_FIELDS) - 1
        if ((self.user.has_confirmed_email()) and (step == self.activation_step)):
            # Profile is valid. Activate in this language.
            languages = self.get_active_languages()
            if not (lang in languages):
                languages.append(lang)
                self._set_active_languages(languages=languages)
        else:
            error_messages.append(_("Please confirm your email address."))
        self.save(update_fields={'active_languages'})
        return step, error_messages

    def get_matching_rank(self, other_profile, second_call=True) -> int:
        self.validate_profile_and_activate()
        other_profile.validate_profile_and_activate()
        if self.is_active and other_profile.is_active:
            if Block.objects.there_is_block(user_1=self.user, user_2=other_profile.user):
                return self.__class__.RANK_0
            other_user_age = get_age(other_profile.user.date_of_birth)
            if other_profile.user.gender not in self.gender_to_match:
                return self.__class__.RANK_0
            if not self.min_age_match <= other_user_age <= self.max_age_match:
                return self.__class__.RANK_0
            if (other_profile.user.diet == User.DIET_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.smoking == self.__class__.SMOKING_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.marital_status == self.__class__.MARITAL_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            diet_rank = self.diet_match.get(str(other_profile.user.diet), self.__class__.RANK_5)
            smoking_rank = self.smoking_match.get(str(other_profile.smoking), self.__class__.RANK_5)
            marital_status_rank = self.marital_status_match.get(str(other_profile.marital_status), self.__class__.RANK_5)
            rank = min([diet_rank, smoking_rank, marital_status_rank])
            if (rank > self.__class__.RANK_0) and (second_call):
                other_user_rank = other_profile.get_matching_rank(other_profile=self, second_call=False)
                if (other_user_rank == self.__class__.RANK_0):
                    rank = self.__class__.RANK_0
            other_profile.rank = rank
            return rank
        else:
            return self.__class__.RANK_0

    @property
    def is_active(self):
        return self.user.is_active and get_language() in self.get_active_languages()

    def deactivate(self):
        self._set_active_languages([])
        self.activation_step = 0
        self.save(update_fields={'active_languages', 'activation_step'})

    def get_name(self):
        # Speedy Match name is user's first name.
        return self.user.get_first_name()

