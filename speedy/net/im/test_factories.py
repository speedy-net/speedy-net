import factory

from speedy.net.accounts.test_factories import UserFactory
from .models import Chat


class ChatFactory(factory.DjangoModelFactory):
    site_id = 1

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not extracted:
            extracted = [UserFactory(),
                         UserFactory()]

        if extracted:
            for group in extracted:
                self.participants.add(group)

    class Meta:
        model = Chat
