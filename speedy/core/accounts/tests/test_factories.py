import string
from datetime import date

import factory
import factory.fuzzy

from django.contrib.sites.models import Site
from django.conf import settings

from speedy.core.accounts.models import normalize_username, User, UserEmailAddress


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
    def deactivate_profile(self, create, extracted, **kwargs):
        # Deactivate only on speedy.net, speedy.match default is inactive.
        site = Site.objects.get_current()
        speedy_net_site_id = settings.SITE_PROFILES.get('net').get('site_id')
        if site.id == speedy_net_site_id:
            self.profile.deactivate()


class UserFactory(DefaultUserFactory):
    @factory.post_generation
    def activate_profile(self, create, extracted, **kwargs):
        self.profile.activate()
        site = Site.objects.get_current()
        speedy_match_site_id = settings.SITE_PROFILES.get('match').get('site_id')
        if site.id == speedy_match_site_id:
            net_profile = self.get_profile(model=None, profile_model=settings.SITE_PROFILES.get('net').get('site_profile_model'))
            net_profile.activate()


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.Faker('email')

    class Meta:
        model = UserEmailAddress
