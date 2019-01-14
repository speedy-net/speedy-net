import string
from datetime import date

import factory
import factory.fuzzy

from django.conf import settings as django_settings
from django.test import TestCase as DjangoTestCase

from speedy.core.base.test import tests_settings
from speedy.core.base.utils import normalize_username
from speedy.core.accounts.models import User, UserEmailAddress


if (django_settings.LOGIN_ENABLED):
    _test_case = DjangoTestCase()


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

        @factory.post_generation
        def validate_first_and_last_name_in_all_languages(self, created, extracted, **kwargs):
            _test_case.assertTupleEqual(tuple1=User.LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name'))
            _test_case.assertEqual(first=self.first_name_en, second=self.first_name)
            _test_case.assertEqual(first=self.first_name_he, second=self.first_name)
            _test_case.assertEqual(first=self.last_name_en, second=self.last_name)
            _test_case.assertEqual(first=self.last_name_he, second=self.last_name)
            field_name_localized_list = list()
            for base_field_name in User.LOCALIZABLE_FIELDS:
                for language_code in django_settings.ALL_LANGUAGE_CODES:
                    field_name_localized = '{}_{}'.format(base_field_name, language_code)
                    _test_case.assertEqual(first=getattr(self, field_name_localized), second=getattr(self, base_field_name), msg="DefaultUserFactory::fields don't match ({field_name_localized}, {base_field_name}), self.pk={self_pk}, self.username={self_username}, self.slug={self_slug}, self.profile.get_name()={self_profile_get_name}".format(
                        field_name_localized=field_name_localized,
                        base_field_name=base_field_name,
                        self_pk=self.pk,
                        self_username=self.username,
                        self_slug=self.slug,
                        self_profile_get_name=self.profile.get_name(),
                    ))
                    field_name_localized_list.append(field_name_localized)
            _test_case.assertListEqual(list1=field_name_localized_list, list2=['first_name_en', 'first_name_he', 'last_name_en', 'last_name_he'])


