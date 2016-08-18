from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)

    def __init__(self, **kwargs):
        self.from_entity = kwargs.pop('from_entity', None)
        self.to_entity = kwargs.pop('to_entity', None)
        self.chat = kwargs.pop('chat', None)
        assert bool(self.from_entity and self.to_entity) != bool(self.from_entity and self.chat)
        super().__init__(**kwargs)
        self.helper = FormHelper()
        if self.chat:
            self.helper.form_action = reverse('im:chat_send',
                                              kwargs={'username': self.from_entity.slug,
                                                      'chat_pk': self.chat.id})
        self.helper.form_class = 'form-vertical'
        self.helper.layout = Layout(
            InlineField('text', style="height: 55px"),
            Submit('submit', _('Send')),
        )

    def save(self, commit=True):
        assert commit
        return Message.objects.send_message(from_entity=self.from_entity, to_entity=self.to_entity, chat=self.chat, text=self.cleaned_data['text'])
