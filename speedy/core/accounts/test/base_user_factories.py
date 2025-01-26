from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import string
        from datetime import date
        from typing import TYPE_CHECKING

        import factory
        import factory.fuzzy

        from django import test as django_test

        from speedy.core.base.test import tests_settings
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin

        from speedy.core.base.utils import normalize_username
        from speedy.core.accounts.models import User

        UserTypeHintMixin = object
        if TYPE_CHECKING:
            UserTypeHintMixin = User


        class DjangoTestCaseWithMixin(SpeedyCoreAccountsModelsMixin, django_test.TestCase):
            pass


        _test_case_with_mixin = DjangoTestCaseWithMixin()


        class DefaultUserFactory(factory.django.DjangoModelFactory, UserTypeHintMixin):
            """
            This factory is used to create users who are active on Speedy Net, but inactive on Speedy Match.
            """
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
            _save = factory.PostGenerationMethodCall(method_name='save')  # Call save after set_password

            class Meta:
                model = User
                skip_postgeneration_save = True  # Avoid warning in factory-boy>=3.3,<4.0

            @factory.post_generation
            def validate_first_and_last_name_in_all_languages(self, created, extracted, **kwargs):
                _test_case_with_mixin.assert_user_first_and_last_name_in_all_languages(user=self)


