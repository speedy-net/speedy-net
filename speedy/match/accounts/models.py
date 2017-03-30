from django.db import models
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
    min_age_match = models.SmallIntegerField(verbose_name=_('minial age to match'), default=0)
    max_age_match = models.SmallIntegerField(verbose_name=_('maximal age to match'), default=180)
    smoking = models.SmallIntegerField(verbose_name=_('smoking'), choices=SMOKING_CHOICES, default=SMOKING_UNKNOWN)
    city = models.CharField(verbose_name=_('city'), max_length=255, null=True)
    marital_status = models.SmallIntegerField(verbose_name=_('Marital status'), choices=MARITAL_STATUS_CHOICES, default=MARITAL_STATUS_UNKNOWN)
    children = models.TextField(verbose_name=_('do you have children?'), null=True)
    more_children = models.TextField(verbose_name=_('do you want (more) children?'), null=True)
    profile_description = models.TextField(verbose_name=_('Few words about me'), null=True)
    match_description = models.TextField(verbose_name=_('My ideal match'), null=True)
    gender_to_match = ArrayField(models.SmallIntegerField(), verbose_name=_('Gender'), size=3, default=[User.GENDER_FEMALE, User.GENDER_MALE, User.GENDER_OTHER])

    diet_match = JSONField(verbose_name=('diet match'), default={})
    smoking_match = JSONField(verbose_name=('smoking match'), default={})
    marital_match = JSONField(verbose_name=_('marital match'), default={})
    activation_step = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Speedy Match Profile'
        verbose_name_plural = 'Speedy Match Profiles'

    def get_active_languages(self):
        return list(filter(None, (l.strip() for l in self.active_languages.split(','))))

    def set_active_languages(self, languages):
        self.active_languages = ','.join(set(languages))

    def activate(self):
        languages = self.get_active_languages()
        languages.append(get_language())
        self.set_active_languages(languages)
        self.save(update_fields={'active_languages'})

    def matching_function(self, other_profile, second_call=True) -> int:
        other_user_age = get_age(other_profile.user.date_of_birth)
        if other_profile.user.gender not in self.gender_to_match:
            return self.RANK_0
        if not self.min_age_match <= other_user_age <= self.max_age_match:
            return self.RANK_0
        diet_rank = self.diet_match.get(other_profile.user.diet, self.RANK_5)
        smoking_rank = self.smoking_match.get(other_profile.smoking, self.RANK_5)
        marital_rank = self.marital_match.get(other_profile.marital_status, self.RANK_5)
        rank = min([diet_rank, smoking_rank, marital_rank])
        if ((rank > self.RANK_0) and (second_call)):
            other_user_rank = other_profile.matching_function(other_profile=self, second_call=False)
            if (other_user_rank == self.RANK_0):
                rank = self.RANK_0
        other_profile.rank = rank
        return rank

    @property
    def is_active(self):
        speedy_net_profile = self.user.get_profile(model=SpeedyNetSiteProfile)
        return speedy_net_profile.is_active and get_language() in self.get_active_languages()

    def deactivate(self):
        self.set_active_languages([])
        self.save(update_fields={'active_languages'})
