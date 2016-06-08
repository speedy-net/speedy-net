import factory

from .models import User, UserEmailAddress


class UserFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    gender = User.GENDER_OTHER

    password = factory.PostGenerationMethodCall('set_password', '111')

    class Meta:
        model = User


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.Faker('email')

    class Meta:
        model = UserEmailAddress
