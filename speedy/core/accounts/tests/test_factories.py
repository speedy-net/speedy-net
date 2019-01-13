import string
import random
from datetime import date

import factory
import factory.fuzzy

# from unittest import TestCase as PythonTestCase #### TODO

from django.conf import settings as django_settings
# from django.test import TestCase as DjangoTestCase #### TODO
from django.contrib.sites.models import Site

from speedy.core.base.test import tests_settings
# from speedy.core.base.test.models import SiteTestCase #### TODO
from speedy.core.base.utils import normalize_username
from speedy.core.accounts.models import User, UserEmailAddress
from speedy.core.accounts.translation import UserTranslationOptions #### TODO
from speedy.core.accounts.forms import LocalizedFirstLastNameMixin #### TODO


if (django_settings.LOGIN_ENABLED):

    # _test_case = PythonTestCase()
    # _test_case = DjangoTestCase()
    # _test_case = SiteTestCase()
    # _test_case.set_up()


    class UserConfirmedEmailAddressFactory(factory.DjangoModelFactory):
        email = factory.Faker('email')
        is_confirmed = True

        class Meta:
            model = UserEmailAddress


    # class DefaultUserFactory(factory.DjangoModelFactory, PythonTestCase): # ~~~~ TODO
    # class DefaultUserFactory(factory.DjangoModelFactory, DjangoTestCase): # ~~~~ TODO
    # class DefaultUserFactory(factory.DjangoModelFactory, SiteTestCase):
    # class DefaultUserFactory(PythonTestCase, factory.DjangoModelFactory): # ~~~~ TODO
    # class DefaultUserFactory(DjangoTestCase, factory.DjangoModelFactory): # ~~~~ TODO
    # class DefaultUserFactory(SiteTestCase, factory.DjangoModelFactory):
    class DefaultUserFactory(factory.DjangoModelFactory):
        first_name = factory.Faker('first_name')
        last_name = factory.Faker('last_name')
        date_of_birth = factory.fuzzy.FuzzyDate(start_date=date(year=1900, month=1, day=1))
        gender = factory.fuzzy.FuzzyChoice(choices=User.GENDER_VALID_VALUES)
        slug = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
        username = factory.LazyAttribute(lambda o: normalize_username(username=o.slug))
        password = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
        _password = factory.PostGenerationMethodCall(method_name='set_password', raw_password=tests_settings.USER_PASSWORD)

        class Meta:
            model = User

        # @factory.post_generation
        # def validate_first_and_last_name_in_all_languages(self, create, extracted, **kwargs):
        #     localizable_fields = UserTranslationOptions.fields
        #     # ~~~~ TODO: use assert
        #     # assert localizable_fields == LocalizedFirstLastNameMixin.get_localizable_fields()
        #     _test_case.assertListEqual(list1=sorted(list(localizable_fields)), list2=sorted(list(LocalizedFirstLastNameMixin.get_localizable_fields())))
        #     _test_case.assertListEqual(list1=sorted(list(localizable_fields)), list2=sorted(['first_name', 'last_name']))
        #     _test_case.assertSetEqual(set1=set(localizable_fields), set2=set(LocalizedFirstLastNameMixin.get_localizable_fields()))
        #     _test_case.assertSetEqual(set1=set(localizable_fields), set2={'first_name', 'last_name'})
        #     # _test_case.assertTupleEqual(tuple1=localizable_fields, tuple2=LocalizedFirstLastNameMixin.get_localizable_fields())
        #     # _test_case.assertTupleEqual(tuple1=localizable_fields, tuple2=('first_name', 'last_name'))
        #     # TODO - uncomment these lines
        #     # _test_case.assertEqual(first=self.first_name_en, second=self.first_name)
        #     # _test_case.assertEqual(first=self.first_name_he, second=self.first_name)
        #     # _test_case.assertEqual(first=self.last_name_en, second=self.last_name)
        #     # _test_case.assertEqual(first=self.last_name_he, second=self.last_name)
        #     field_name_localized_list = list()
        #     for base_field_name in localizable_fields:
        #         for language_code in _test_case.all_languages_code_list:
        #             field_name_localized = '{}_{}'.format(base_field_name, language_code)
        #             _test_case.assertEqual(first=getattr(self, field_name_localized), second=getattr(self, base_field_name), msg=None)
        #             field_name_localized_list.append(field_name_localized)
        #     self.assertListEqual(list1=field_name_localized_list, list2=[])
        #     _test_case.assertEqual(first=self.first_name_en, second=self.first_name)
        #     _test_case.assertEqual(first=self.first_name_he, second=self.first_name)
        #     _test_case.assertEqual(first=self.last_name_en, second=self.last_name)
        #     _test_case.assertEqual(first=self.last_name_he, second=self.last_name)
        #

    class InactiveUserFactory(DefaultUserFactory):
        @factory.post_generation
        def deactivate_speedy_net_profile(self, create, extracted, **kwargs):
            # Deactivate only on speedy.net, speedy.match default is inactive.
            site = Site.objects.get_current()
            if (site.id == django_settings.SPEEDY_NET_SITE_ID):
                self.profile.deactivate()


    class ActiveUserFactory(DefaultUserFactory):
        @factory.post_generation
        def activate_profile(self, create, extracted, **kwargs):
            site = Site.objects.get_current()
            if (site.id == django_settings.SPEEDY_MATCH_SITE_ID):
                # ~~~~ TODO: this code is specific for Speedy Match, should not be in core.
                # ~~~~ TODO: maybe change ".profile" to ".speedy_match_profile"?
                from speedy.core.uploads.tests.test_factories import UserImageFactory
                from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
                self.profile.profile_description = "Hi!"
                self.profile.city = "Tel Aviv."
                self.profile.children = "One boy."
                self.profile.more_children = "Yes."
                self.profile.match_description = "Hi!"
                self.profile.height = random.randint(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_ALLOWED, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_ALLOWED)
                _test_case.assertEqual(first=self.diet, second=User.DIET_UNKNOWN)
                _test_case.assertEqual(first=self.diet, second=User.DIET_UNKNOWN - 1) # ~~~~ TODO: remove this line!
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
                if (not (step == len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
                    raise Exception("Step not as expected, {}".format(step))
                # print(self.gender, self.diet, self.profile.smoking_status, self.profile.marital_status, self.profile.height) # ~~~~ TODO: remove this line!
                # print(tests_settings.USER_PASSWORD) # ~~~~ TODO: remove this line!
            else:
                self.profile.activate()
                # print(self.gender, self.diet) # ~~~~ TODO: remove this line!
                # print(tests_settings.USER_PASSWORD) # ~~~~ TODO: remove this line!


    class UserEmailAddressFactory(factory.DjangoModelFactory):
        user = factory.SubFactory(DefaultUserFactory)
        email = factory.Faker('email')

        class Meta:
            model = UserEmailAddress


