from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language

from speedy.core.accounts.models import SiteProfileBase, ACCESS_FRIENDS, ACCESS_ANYONE
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile


class SiteProfile(SiteProfileBase):

    DIET_VEGAN = 1
    DIET_VEGETARIAN = 2
    DIET_CARNIST = 3
    DIET_CHOICES = (
        (DIET_VEGAN, _('Vegan (eats only plants and fungi)')),
        (DIET_VEGETARIAN, _('Vegetarian (doesn\'t eat fish and meat)')),
        (DIET_CARNIST, _('Carnist (eats animals)'))
    )

    SMOKING_YES = 0
    SMOKING_NO = 1
    SMOKING_SOMETIMES = 2
    SMOKING_CHOICES = (
        (SMOKING_YES, _('Yes')),
        (SMOKING_NO, _('No')),
        (SMOKING_SOMETIMES, _('Sometimes'))
    )
    MARITAL_STATUS_SINGLE = 0
    MARITAL_STATUS_DIVORCED = 1
    MARITAL_STATUS_WIDOWED = 2
    MARITAL_STATUS_IN_RELATIONSHIP = 3
    MARITAL_STATUS_IN_OPEN_RELATIONSHIP = 4
    MARITAL_STATUS_COMPLICATED = 5
    MARITAL_STATUS_SEPARATED = 6
    MARITAL_STATUS_MARRIED= 7

    MARITAL_STATUS_CHOICES = (
        (MARITAL_STATUS_SINGLE, _('Single')),
        (MARITAL_STATUS_DIVORCED, _('Divorced')),
        (MARITAL_STATUS_WIDOWED, _('Widowed')),
        (MARITAL_STATUS_IN_RELATIONSHIP, _('In a relatioship')),
        (MARITAL_STATUS_IN_OPEN_RELATIONSHIP, _('In an open relationship')),
        (MARITAL_STATUS_COMPLICATED, _('Complicated')),
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

    access_account = ACCESS_FRIENDS
    access_dob_day_month = ACCESS_ANYONE
    access_dob_year = ACCESS_ANYONE
    notify_on_message = models.PositiveIntegerField(verbose_name=_('on new messages'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    notify_on_like = models.PositiveIntegerField(verbose_name=_('on new likes'), choices=SiteProfileBase.NOTIFICATIONS_CHOICES, default=SiteProfileBase.NOTIFICATIONS_ON)
    active_languages = models.TextField(verbose_name=_('active languages'), blank=True)

    men_to_match = models.NullBooleanField(verbose_name=_('Interested in men'), null=True)
    women_to_match = models.NullBooleanField(verbose_name=_('Interested in women'), default=True)
    other_to_match = models.NullBooleanField(verbose_name=_('Interested in others'), default=True)
    height = models.SmallIntegerField(verbose_name=_('Height'), null=True)
    diet = models.SmallIntegerField(verbose_name=_('Diet'), choices=DIET_CHOICES, null=True)
    min_age_match = models.SmallIntegerField(verbose_name=_('Minial age to match'), null=True)
    max_age_match = models.SmallIntegerField(verbose_name=_('Minial age to match'), null=True)
    smoking = models.SmallIntegerField(verbose_name=_('Smoking'), choices=SMOKING_CHOICES, null=True)
    city = models.CharField(verbose_name=_('City'), max_length=255, null=True)
    marital_status = models.SmallIntegerField(verbose_name=_('Marital status'), choices=MARITAL_STATUS_CHOICES, null=True)
    children = models.TextField(verbose_name=_('Do you have children?'), null=True)
    more_children = models.TextField(verbose_name=_('Do you want (more) children?'), null=True)
    profile_desription = models.TextField(verbose_name=_('About myself'), null=True)

    diet_vegan_match = models.SmallIntegerField(verbose_name=_('Vegan match'), choices=RANK_CHOICES, default=RANK_5)
    diet_vegetarian_match = models.SmallIntegerField(verbose_name=_('Vegetarian match'), choices=RANK_CHOICES, default=RANK_5)
    diet_carnist_match = models.SmallIntegerField(verbose_name=_('Carnist match'), choices=RANK_CHOICES, default=RANK_5)
    smoking_yes_match = models.SmallIntegerField(verbose_name=_('Smoking match'), choices=RANK_CHOICES, default=RANK_5)
    smoking_no_match = models.SmallIntegerField(verbose_name=_('No smoking match'), choices=RANK_CHOICES, default=RANK_5)
    smoking_sometimes_match = models.SmallIntegerField(verbose_name=_('Sometimes smoking match'), choices=RANK_CHOICES, default=RANK_5)
    marital_single_match = models.SmallIntegerField(verbose_name=_('Singles match'), choices=RANK_CHOICES, default=RANK_5)
    marital_divorced_match = models.SmallIntegerField(verbose_name=_('Divorced match'), choices=RANK_CHOICES, default=RANK_5)
    marital_widowed_match = models.SmallIntegerField(verbose_name=_('Widowed match'), choices=RANK_CHOICES, default=RANK_5)
    marital_relationship_match = models.SmallIntegerField(verbose_name=_('I an relationship match'), choices=RANK_CHOICES, default=RANK_5)
    marital_open_relationship_match = models.SmallIntegerField(verbose_name=_('I an open relationship match'), choices=RANK_CHOICES, default=RANK_5)
    marital_complicated_match = models.SmallIntegerField(verbose_name=_('I an complicated relationship match'), choices=RANK_CHOICES, default=RANK_5)
    marital_separated_match = models.SmallIntegerField(verbose_name=_('Separated match'), choices=RANK_CHOICES, default=RANK_5)
    marital_married_match = models.SmallIntegerField(verbose_name=_('Married match'), choices=RANK_CHOICES, default=RANK_5)

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

    @property
    def is_active(self):
        speedy_net_profile = self.user.get_profile(model=SpeedyNetSiteProfile)
        return speedy_net_profile.is_active and get_language() in self.get_active_languages()

    def deactivate(self):
        self.set_active_languages([])
        self.save(update_fields={'active_languages'})
