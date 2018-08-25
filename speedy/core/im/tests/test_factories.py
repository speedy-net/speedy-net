import factory

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from ..models import Chat


class ChatFactory(factory.DjangoModelFactory):
    ent1 = factory.SubFactory(ActiveUserFactory)
    ent2 = factory.SubFactory(ActiveUserFactory)

    class Meta:
        model = Chat

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if extracted:
            self.is_group = True
            for entity in extracted:
                self.group.add(entity)


