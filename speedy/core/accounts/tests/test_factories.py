import string
from datetime import date

import factory
import factory.fuzzy

from django.contrib.sites.models import Site
from django.conf import settings

from speedy.core.accounts.models import normalize_username, User, UserEmailAddress
from speedy.core.uploads.models import Image


class DefaultUserFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    date_of_birth = factory.fuzzy.FuzzyDate(start_date=date(1900, 1, 1))
    gender = User.GENDER_OTHER
    slug = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
    username = factory.LazyAttribute(lambda o: normalize_username(slug=o.slug))

    password = factory.PostGenerationMethodCall('set_password', '111')

    class Meta:
        model = User


class InactiveUserFactory(DefaultUserFactory):

    @factory.post_generation
    def deactivate_speedy_net_profile(self, create, extracted, **kwargs):
        # Deactivate only on speedy.net, speedy.match default is inactive.
        site = Site.objects.get_current()
        speedy_net_site_id = settings.SITE_PROFILES.get('net').get('site_id')
        if (site.id == speedy_net_site_id):
            self.profile.deactivate()


class UserConfirmedEmailAddressFactory(factory.DjangoModelFactory):
    email = factory.Faker('email')
    is_confirmed = True

    class Meta:
        model = UserEmailAddress


class UserImageFactory(factory.DjangoModelFactory):

    file = factory.django.ImageField()

    class Meta:
        model = Image


class ActiveUserFactory(DefaultUserFactory):

    @factory.post_generation
    def activate_profile(self, create, extracted, **kwargs):
        site = Site.objects.get_current()
        speedy_match_site_id = settings.SITE_PROFILES.get('match').get('site_id')
        if (site.id == speedy_match_site_id):
            # ~~~~ TODO: this code is specific for Speedy Match, should not be in core.
            from speedy.match.accounts.models import SiteProfile
            self.profile.profile_description = "Hi!"
            self.profile.city = "Tel Aviv."
            self.profile.children = "One boy."
            self.profile.more_children = "Yes."
            self.profile.match_description = "Hi!"
            self.profile.height = 170
            if (self.diet == User.DIET_UNKNOWN):
                self.diet = User.DIET_VEGAN
            self.profile.smoking = SiteProfile.SMOKING_NO
            self.profile.marital_status = SiteProfile.MARITAL_STATUS_SINGLE
            self.profile.gender_to_match = [User.GENDER_OTHER]
            self.photo = UserImageFactory(owner=self)
            self.profile.activation_step = 7
            email = UserConfirmedEmailAddressFactory(user=self)
            email.save()
            self.save()
            self.profile.save()
            self._profile = self.get_profile()
            step, error_messages = self.profile.validate_profile_and_activate()
            if (not (step == len(settings.SITE_PROFILE_FORM_FIELDS))):
                raise Exception("Step not as expected, {}".format(step))
            if (len(error_messages) > 0):
                raise Exception("Error messages not as expected, {}".format(", ".join(str(error_messages))))
            # # self.profile._set_active_languages(["en"])
            # # self.profile.save(update_fields={'active_languages', 'activation_step'})
            # ~~~~ TODO: remove the following lines, user can't be activated without executing self.profile.validate_profile_and_activate()
            # self.profile._set_active_languages(["en"])
            # self.profile.save(update_fields={'active_languages', 'activation_step'})
        else:
            self.profile.activate()


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(ActiveUserFactory)
    email = factory.Faker('email')

    class Meta:
        model = UserEmailAddress
