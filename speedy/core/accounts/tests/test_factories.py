import string
import random
from datetime import date

import factory
import factory.fuzzy

from django.conf import settings
# from django.test import TestCase as DjangoTestCase #### TODO
from django.contrib.sites.models import Site

from speedy.core.base.test import TestCase #### TODO
from ..models import normalize_username, User, UserEmailAddress
from ..translation import UserTranslationOptions #### TODO
from ..forms import LocalizedFirstLastNameMixin #### TODO


def get_random_user_password_length():
    return random.randint(User.MIN_PASSWORD_LENGTH, User.MAX_PASSWORD_LENGTH)


def get_random_user_password():
    user_password_length = get_random_user_password_length()
    user_password = ''.join(random.choice(string.digits + string.ascii_letters + string.punctuation + ' ') for _i in range(user_password_length))
    if (len(user_password) == user_password_length):
        return user_password
    else:
        raise Exception("Unexpected: len(user_password)={}, user_password_length={}".format(len(user_password), user_password_length))


# ~~~~ TODO: move to base test.
# Generate a new random password for each test.
USER_PASSWORD = get_random_user_password()
# USER_PASSWORD = 'vjha9c4q44zs'


class UserConfirmedEmailAddressFactory(factory.DjangoModelFactory):
    email = factory.Faker('email')
    is_confirmed = True

    class Meta:
        model = UserEmailAddress


# class DefaultUserFactory(factory.DjangoModelFactory, DjangoTestCase): # ~~~~ TODO
# class DefaultUserFactory(factory.DjangoModelFactory, TestCase):
# class DefaultUserFactory(DjangoTestCase, factory.DjangoModelFactory): # ~~~~ TODO
# class DefaultUserFactory(TestCase, factory.DjangoModelFactory):
class DefaultUserFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    date_of_birth = factory.fuzzy.FuzzyDate(start_date=date(year=1900, month=1, day=1))
    gender = factory.fuzzy.FuzzyChoice(choices=User.GENDER_VALID_VALUES)
    slug = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
    username = factory.LazyAttribute(lambda o: normalize_username(slug=o.slug))
    password = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
    _password = factory.PostGenerationMethodCall(method_name='set_password', raw_password=USER_PASSWORD)

    class Meta:
        model = User

    # @factory.post_generation
    # def validate_first_and_last_name_in_all_languages(self, create, extracted, **kwargs):
    #     localizable_fields = UserTranslationOptions.fields
    #     # ~~~~ TODO: use assert
    #     assert localizable_fields == LocalizedFirstLastNameMixin.get_localizable_fields()
    #     self.assertEqual(first=localizable_fields, second=LocalizedFirstLastNameMixin.get_localizable_fields())
    #     self.assertEqual(first=localizable_fields, second=('first_name', 'last_name'))
    #     self.assertEqual(first=localizable_fields, second=('first_name', 'last_name', '1'))####
    #     # self.assertEqual(first=self.first_name_en, second=self.first_name)
    #     # self.assertEqual(first=self.first_name_he, second=self.first_name)
    #     # self.assertEqual(first=self.last_name_en, second=self.last_name)
    #     # self.assertEqual(first=self.last_name_he, second=self.last_name)
    #     field_name_localized_list = list()
    #     for base_field_name in localizable_fields:
    #         for language_code in self.all_languages_code_list:
    #             field_name_localized = '{}_{}'.format(base_field_name, language_code)
    #             self.assertEqual(first=getattr(self, field_name_localized), second=getattr(self, base_field_name), msg=None)
    #             field_name_localized_list.append(field_name_localized)
    #     self.assertListEqual(list1=field_name_localized_list, list2=[])
    #     self.assertEqual(first=self.first_name_en, second=self.first_name)
    #     self.assertEqual(first=self.first_name_he, second=self.first_name)
    #     self.assertEqual(first=self.last_name_en, second=self.last_name)
    #     self.assertEqual(first=self.last_name_he, second=self.last_name)
    #

class InactiveUserFactory(DefaultUserFactory):
    @factory.post_generation
    def deactivate_speedy_net_profile(self, create, extracted, **kwargs):
        # Deactivate only on speedy.net, speedy.match default is inactive.
        site = Site.objects.get_current()
        if (site.id == settings.SPEEDY_NET_SITE_ID):
            self.profile.deactivate()


class ActiveUserFactory(DefaultUserFactory):
    @factory.post_generation
    def activate_profile(self, create, extracted, **kwargs):
        site = Site.objects.get_current()
        if (site.id == settings.SPEEDY_MATCH_SITE_ID):
            # ~~~~ TODO: this code is specific for Speedy Match, should not be in core.
            from speedy.core.uploads.tests.test_factories import UserImageFactory
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
            self.profile.profile_description = "Hi!"
            self.profile.city = "Tel Aviv."
            self.profile.children = "One boy."
            self.profile.more_children = "Yes."
            self.profile.match_description = "Hi!"
            self.profile.height = random.randint(settings.MIN_HEIGHT_ALLOWED, settings.MAX_HEIGHT_ALLOWED)
            # self.assertEqual(first=self.diet, second=User.DIET_UNKNOWN)
            # self.assertEqual(first=self.diet, second=User.DIET_UNKNOWN - 1) # ~~~~ TODO: remove this line!
            if (self.diet == User.DIET_UNKNOWN):
                self.diet = random.choice(User.DIET_VALID_VALUES)
            else:
                raise Exception("Unexpected: diet={}".format(self.diet))
            # self.diet = random.choice(User.DIET_VALID_VALUES)
            # self.assertNotEqual(first=self.diet, second=User.DIET_UNKNOWN)
            if (self.profile.smoking_status == SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN):
                self.profile.smoking_status = random.choice(SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES)
            else:
                raise Exception("Unexpected: smoking_status={}".format(self.profile.smoking_status))
            if (self.profile.marital_status == SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN):
                self.profile.marital_status = random.choice(SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES)
            else:
                raise Exception("Unexpected: marital_status={}".format(self.profile.marital_status))
            self.profile.gender_to_match = User.GENDER_VALID_VALUES
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
            # print(self.gender, self.diet, self.profile.smoking_status, self.profile.marital_status, self.profile.height) # ~~~~ TODO: remove this line!
            # print(USER_PASSWORD) # ~~~~ TODO: remove this line!
        else:
            self.profile.activate()
            # print(self.gender, self.diet) # ~~~~ TODO: remove this line!
            # print(USER_PASSWORD) # ~~~~ TODO: remove this line!


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(ActiveUserFactory)
    email = factory.Faker('email')

    class Meta:
        model = UserEmailAddress


