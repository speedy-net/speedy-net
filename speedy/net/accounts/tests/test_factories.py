import string
from datetime import date

import factory
import factory.fuzzy

from ..models import normalize_username, User, UserEmailAddress


class UserFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    date_of_birth = factory.fuzzy.FuzzyDate(start_date=date(1900, 1, 1))
    gender = User.GENDER_OTHER
    slug = factory.fuzzy.FuzzyText(chars=string.ascii_lowercase)
    username = factory.LazyAttribute(lambda o: normalize_username(o.slug))

    password = factory.PostGenerationMethodCall('set_password', '111')

    class Meta:
        model = User


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.Faker('email')

    class Meta:
        model = UserEmailAddress
