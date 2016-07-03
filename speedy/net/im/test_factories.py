import factory

from .models import Chat


class ChatFactory(factory.DjangoModelFactory):
    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if extracted:
            for entity in extracted:
                self.group.add(entity)

    class Meta:
        model = Chat
