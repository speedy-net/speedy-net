import factory

from speedy.net.accounts.test_factories import UserFactory
from .models import Chat


class ChatFactory(factory.DjangoModelFactory):
    ent1 = factory.SubFactory(UserFactory)
    ent2 = factory.SubFactory(UserFactory)

    class Meta:
        model = Chat

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if extracted:
            self.is_group = True
            for entity in extracted:
                self.group.add(entity)

