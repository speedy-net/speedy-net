import string
from datetime import date

from django.conf import settings as django_settings
from django import test as django_test

if (django_settings.TESTS):
    from speedy.core.base.test import tests_settings
    from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin
    from speedy.core.base.utils import normalize_username
    from speedy.core.accounts.models import User

    import factory
    import factory.fuzzy

    if (django_settings.LOGIN_ENABLED):
        class DjangoTestCaseWithMixin(SpeedyCoreAccountsModelsMixin, django_test.TestCase):
            pass


        _test_case_with_mixin = DjangoTestCaseWithMixin()


        class DefaultUserFactory(factory.django.DjangoModelFactory):
            first_name_en = factory.Faker('first_name')
            last_name_en = factory.Faker('last_name')
            first_name_he = factory.LazyAttribute(lambda o: o.first_name_en)
            last_name_he = factory.LazyAttribute(lambda o: o.last_name_en)
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
                _test_case_with_mixin.assert_user_first_and_last_name_in_all_languages(user=self)


