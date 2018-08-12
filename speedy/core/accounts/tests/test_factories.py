import string
import random
from datetime import date

import factory
import factory.fuzzy

from django.contrib.sites.models import Site
from django.conf import settings

from speedy.core.accounts.models import normalize_username, User, UserEmailAddress
from speedy.core.uploads.models import Image


# Generate a new random password for each test.
USER_PASSWORD_LENGTH = random.randint(User.MIN_PASSWORD_LENGTH, User.MAX_PASSWORD_LENGTH)
USER_PASSWORD = ''.join(random.choice(string.digits + string.ascii_letters + string.punctuation + ' ') for _i in range(USER_PASSWORD_LENGTH))
# USER_PASSWORD = 'vjha9c4q44zs'


class DefaultUserFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    date_of_birth = factory.fuzzy.FuzzyDate(start_date=date(year=1900, month=1, day=1))
    # ~~~~ TODO: assign values randomly (gender).
    gender = User.GENDER_OTHER
    slug = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
    username = factory.LazyAttribute(lambda o: normalize_username(slug=o.slug))
    password = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
    _password = factory.PostGenerationMethodCall(method_name='set_password', raw_password=USER_PASSWORD)

    class Meta:
        model = User


class InactiveUserFactory(DefaultUserFactory):
    @factory.post_generation
    def deactivate_speedy_net_profile(self, create, extracted, **kwargs):
        # Deactivate only on speedy.net, speedy.match default is inactive.
        site = Site.objects.get_current()
        SPEEDY_NET_SITE_ID = settings.SITE_PROFILES.get('net').get('site_id')
        if (site.id == SPEEDY_NET_SITE_ID):
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
        SPEEDY_MATCH_SITE_ID = settings.SITE_PROFILES.get('match').get('site_id')
        if (site.id == SPEEDY_MATCH_SITE_ID):
            # ~~~~ TODO: this code is specific for Speedy Match, should not be in core.
            # ~~~~ TODO: assign values randomly (height, diet, smoking, gender etc).
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
            self.profile.profile_description = "Hi!"
            self.profile.city = "Tel Aviv."
            self.profile.children = "One boy."
            self.profile.more_children = "Yes."
            self.profile.match_description = "Hi!"
            self.profile.height = random.randint(settings.MIN_HEIGHT_ALLOWED, settings.MAX_HEIGHT_ALLOWED)
            if (self.diet == User.DIET_UNKNOWN):
                self.diet = User.DIET_VEGAN
            self.profile.smoking_status = SpeedyMatchSiteProfile.SMOKING_STATUS_NO
            self.profile.marital_status = SpeedyMatchSiteProfile.MARITAL_STATUS_SINGLE
            self.profile.gender_to_match = [User.GENDER_OTHER]
            self.photo = UserImageFactory(owner=self)
            self.profile.activation_step = 9
            email = UserConfirmedEmailAddressFactory(user=self)
            email.save()
            self.save_user_and_profile()
            step, error_messages = self.profile.validate_profile_and_activate()
            if (len(error_messages) > 0):
                raise Exception("Error messages not as expected, {}".format(error_messages))
            if (not (step == len(settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
                raise Exception("Step not as expected, {}".format(step))
        else:
            self.profile.activate()


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(ActiveUserFactory)
    email = factory.Faker('email')

    class Meta:
        model = UserEmailAddress
