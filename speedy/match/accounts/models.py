from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _, get_language

from speedy.core.accounts.models import SiteProfileBase, ACCESS_FRIENDS, ACCESS_ANYONE, User
from speedy.core.base.utils import get_age
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


class SiteProfile(SiteProfileBase):

    SMOKING_UNKNOWN = 0
    SMOKING_NO = 1
    SMOKING_YES = 2
    SMOKING_SOMETIMES = 3
    SMOKING_MAX_VALUE_PLUS_ONE = 4
    SMOKING_CHOICES = (
        (SMOKING_NO, _('No')),
        (SMOKING_YES, _('Yes')),
        (SMOKING_SOMETIMES, _('Sometimes'))
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
        (MARITAL_STATUS_SINGLE, _('Single')),
        (MARITAL_STATUS_DIVORCED, _('Divorced')),
        (MARITAL_STATUS_WIDOWED, _('Widowed')),
        (MARITAL_STATUS_IN_RELATIONSHIP, _('In a relatioship')),
        (MARITAL_STATUS_IN_OPEN_RELATIONSHIP, _('In an open relationship')),
        (MARITAL_STATUS_COMPLICATED, _('It\'s complicated')),
        (MARITAL_STATUS_SEPARATED, _('Separated')),
        (MARITAL_STATUS_MARRIED, _('Married'))
    )

    RANK_0 = 0
    RANK_1 = 1
    RANK_2 = 2
    RANK_3 = 3
    RANK_4 = 4
    RANK_5 = 5

    RANK_CHOICES = (
        (RANK_0, _('0 stars')),
        (RANK_1, _('1 stars')),
        (RANK_2, _('2 stars')),
        (RANK_3, _('3 stars')),
        (RANK_4, _('4 stars')),
        (RANK_5, _('5 stars'))
    )

    access_account = ACCESS_ANYONE
    access_dob_day_month = ACCESS_ANYONE
    access_dob_year = ACCESS_ANYONE
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    notify_on_like = models.PositiveIntegerField(verbose_name=_('on new likes'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    active_languages = models.TextField(verbose_name=_('active languages'), blank=True)

    height = models.SmallIntegerField(verbose_name=_('height'), null=True)
    min_age_match = models.SmallIntegerField(verbose_name=_('minial age to match'), default=settings.MIN_AGE_ALLOWED)
    max_age_match = models.SmallIntegerField(verbose_name=_('maximal age to match'), default=settings.MAX_AGE_ALLOWED)
    smoking = models.SmallIntegerField(verbose_name=_('smoking status'), choices=SMOKING_CHOICES, default=SMOKING_UNKNOWN)
    city = models.CharField(verbose_name=_('city or locality'), max_length=255, null=True)
    marital_status = models.SmallIntegerField(verbose_name=_('marital status'), choices=MARITAL_STATUS_CHOICES, default=MARITAL_STATUS_UNKNOWN)
    children = models.TextField(verbose_name=_('Do you have children? How many?'), null=True)
    more_children = models.TextField(verbose_name=_('Do you want (more) children?'), null=True)
    profile_description = models.TextField(verbose_name=_('Few words about me'), null=True)
    match_description = models.TextField(verbose_name=_('My ideal match'), null=True)
    gender_to_match = ArrayField(models.SmallIntegerField(), verbose_name=_('Gender'), size=3, default=[])

    diet_match = JSONField(verbose_name=('diet match'), default={
        User.DIET_VEGAN: RANK_5,
        User.DIET_VEGETARIAN: RANK_5,
        User.DIET_CARNIST: RANK_5,
    })
    smoking_match = JSONField(verbose_name=('smoking status match'), default={
        SMOKING_NO: RANK_5,
        SMOKING_YES: RANK_5,
        SMOKING_SOMETIMES: RANK_5,
    })
    marital_status_match = JSONField(verbose_name=_('marital status match'), default={
        MARITAL_STATUS_SINGLE: RANK_5,
        MARITAL_STATUS_DIVORCED: RANK_5,
        MARITAL_STATUS_WIDOWED: RANK_5,
        MARITAL_STATUS_IN_RELATIONSHIP: RANK_5,
        MARITAL_STATUS_IN_OPEN_RELATIONSHIP: RANK_5,
        MARITAL_STATUS_COMPLICATED: RANK_5,
        MARITAL_STATUS_SEPARATED: RANK_5,
        MARITAL_STATUS_MARRIED: RANK_5,
    })
    activation_step = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Speedy Match Profile'
        verbose_name_plural = 'Speedy Match Profiles'

    def _set_active_languages(self, languages):
        languages = sorted(list(set(languages)))
        self.active_languages = ','.join(set(languages))

    def _deactivate_language(self, step):
        lang = get_language()
        self._set_active_languages(set(self.get_active_languages()) - {lang})
        self.activation_step = step
        self.save(update_fields={'active_languages', 'activation_step'})

    def get_active_languages(self):
        return list(filter(None, (l.strip() for l in self.active_languages.split(','))))

    def validate_profile_and_activate(self):
        lang = get_language()
        error_messages = list()
        for step in range(len(settings.SITE_PROFILE_FORM_FIELDS)):
            fields = settings.SITE_PROFILE_FORM_FIELDS[step]
            for field in fields:
                if (field in ['photo']):
                    if (not(self.user.photo)):
                        error_messages.append(_("A profile picture is required."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['profile_description']):
                    if (not(len(self.profile_description) > 0)):
                        error_messages.append(_("Please write some text in this field."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['city']):
                    if (not(len(self.city) > 0)):
                        error_messages.append(_("Please write where you live."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['children']):
                    if (not(len(self.children) > 0)):
                        error_messages.append(_("Do you have children? How many?"))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['more_children']):
                    if (not(len(self.more_children) > 0)):
                        error_messages.append(_("Do you want (more) children?"))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['match_description']):
                    if (not(len(self.match_description) > 0)):
                        error_messages.append(_("Please write some text in this field."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['height']):
                    if (not(1 <= self.height <= 450)):
                        error_messages.append(_("Height must be from 1 to 450 cm."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['diet']):
                    if (not(User.DIET_UNKNOWN < self.user.diet < User.DIET_MAX_VALUE_PLUS_ONE)):
                        error_messages.append(_("Your diet is required."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['smoking']):
                    if (not(self.__class__.SMOKING_UNKNOWN < self.smoking < self.__class__.SMOKING_MAX_VALUE_PLUS_ONE)):
                        error_messages.append(_("Your smoking status is required."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['marital_status']):
                    if (not(self.__class__.MARITAL_STATUS_UNKNOWN < self.marital_status < self.__class__.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)):
                        error_messages.append(_("Your marital status is required."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['gender_to_match']):
                    if (not((len(self.gender_to_match) > 0) and (all((User.GENDER_UNKNOWN <= gender < User.GENDER_MAX_VALUE_PLUS_ONE) for gender in self.gender_to_match)))):
                        self.gender_to_match = []
                        error_messages.append(_("Gender to match is required."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['min_age_match', 'max_age_match']):
                    if (not(settings.MIN_AGE_ALLOWED <= self.min_age_match <= self.max_age_match <= settings.MAX_AGE_ALLOWED)):
                        if (not(settings.MIN_AGE_ALLOWED <= self.min_age_match <= settings.MAX_AGE_ALLOWED)):
                            error_messages.append(_("Minial age to match must be from 0 to 180 years."))
                        if (not(settings.MIN_AGE_ALLOWED <= self.max_age_match <= settings.MAX_AGE_ALLOWED)):
                            error_messages.append(_("Maximal age to match must be from 0 to 180 years."))
                        if (not(self.min_age_match <= self.max_age_match)):
                            error_messages.append(_("Maximal age to match can't be less than minial age to match."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['diet_match']):
                    if (not(all(((diet in self.diet_match) and (self.__class__.RANK_0 <= self.diet_match[diet] <= self.__class__.RANK_5)) for diet in range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)))):
                        # This may be due to values added later.
                        error_messages.append(_("Please select diet match."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['smoking_match']):
                    if (not(all(((smoking in self.smoking_match) and (self.__class__.RANK_0 <= self.smoking_match[smoking] <= self.__class__.RANK_5)) for smoking in range(self.__class__.SMOKING_UNKNOWN + 1, self.__class__.SMOKING_MAX_VALUE_PLUS_ONE)))):
                        # This may be due to values added later.
                        error_messages.append(_("Please select smoking status match."))
                        self._deactivate_language(step=step)
                        return step, error_messages
                elif (field in ['marital_status_match']):
                    if (not(all(((marital_status in self.marital_status_match) and (self.__class__.RANK_0 <= self.marital_status_match[marital_status] <= self.__class__.RANK_5)) for marital_status in range(self.__class__.MARITAL_STATUS_UNKNOWN + 1, self.__class__.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)))):
                        # This may be due to values added later.
                        error_messages.append(_("Please select marital status match."))
                        self._deactivate_language(step=step)
                        return step, error_messages
        step = len(settings.SITE_PROFILE_FORM_FIELDS)
        self.activation_step = step
        languages = self.get_active_languages()
        if (not(lang in languages)):
            languages.append(lang)
            self._set_active_languages(languages=languages)
        self.save(update_fields={'active_languages', 'activation_step'})
        return step, error_messages

    def get_matching_rank(self, other_profile, second_call=True) -> int:
        step, error_messages = self.validate_profile_and_activate()
        other_profile_step, other_profile_error_messages = other_profile.validate_profile_and_activate()
        if ((step == len(settings.SITE_PROFILE_FORM_FIELDS)) and (other_profile_step == len(settings.SITE_PROFILE_FORM_FIELDS))):
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
            diet_rank = self.diet_match.get(other_profile.user.diet, self.__class__.RANK_5)
            smoking_rank = self.smoking_match.get(other_profile.smoking, self.__class__.RANK_5)
            marital_status_rank = self.marital_status_match.get(other_profile.marital_status, self.__class__.RANK_5)
            rank = min([diet_rank, smoking_rank, marital_status_rank])
            if ((rank > self.__class__.RANK_0) and (second_call)):
                other_user_rank = other_profile.get_matching_rank(other_profile=self, second_call=False)
                if (other_user_rank == self.__class__.RANK_0):
                    rank = self.__class__.RANK_0
            other_profile.rank = rank
            return rank
        else:
            return self.__class__.RANK_0

    @property
    def is_active(self):
        speedy_net_profile = self.user.get_profile(model=SpeedyNetSiteProfile)
        return speedy_net_profile.is_active and get_language() in self.get_active_languages()

    def deactivate(self):
        self._set_active_languages([])
        self.activation_step = 0
        self.save(update_fields={'active_languages', 'activation_step'})

    def get_name(self):
        # Speedy Match name is user's first name.
        return self.user.get_first_name()

