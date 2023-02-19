from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Layout, Submit
from django import forms
from django.urls import reverse
from django.utils.translation import pgettext_lazy

from speedy.core.base.forms import FormHelperWithDefaults
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        self.from_entity = kwargs.pop('from_entity', None)
        self.to_entity = kwargs.pop('to_entity', None)
        self.chat = kwargs.pop('chat', None)
        assert bool(self.from_entity and self.to_entity) != bool(self.from_entity and self.chat)
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        if (self.chat):
            self.helper.form_action = reverse('messages:chat_send', kwargs={'chat_slug': self.chat.get_slug(current_user=self.from_entity)})
        else:
            self.helper.form_action = reverse('messages_entity:user_send', kwargs={'slug': self.to_entity.slug})
        self.helper.form_class = 'form-vertical'
        self.helper.layout = Layout(
            InlineField('text', style="height: 55px", onblur='this.value = this.value.trim();'),
            Submit('submit', pgettext_lazy(context=self.from_entity.get_gender(), message='Send')),
        )

    def save(self, commit=True):
        assert commit
        return Message.objects.send_message(from_entity=self.from_entity, to_entity=self.to_entity, chat=self.chat, text=self.cleaned_data['text'])


