import factory

from .models import User

class UserFactory(factory.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'user{0}@example.com'.format(n))
    first_name = 'User'
    last_name = factory.Sequence(lambda n: '#{0}'.format(n))
    gender = User.GENDER_OTHER

    password = factory.PostGenerationMethodCall('set_password', '111')

    class Meta:
        model = User
