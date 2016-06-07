import factory

from .models import User, UserEmailAddress

class UserFactory(factory.DjangoModelFactory):
    first_name = 'User'
    last_name = factory.Sequence(lambda n: '#{0}'.format(n))
    gender = User.GENDER_OTHER

    password = factory.PostGenerationMethodCall('set_password', '111')

    class Meta:
        model = User


class UserEmailAddressFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.Sequence(lambda n: 'email{0}@example.com'.format(n))

    class Meta:
        model = UserEmailAddress
