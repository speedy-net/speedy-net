"""
Forms for the messages app of Speedy Core, which define the message form.
"""
from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Layout, Submit

from django import forms
from django.urls import reverse
from django.utils.translation import pgettext_lazy

from speedy.core.base.forms import FormHelperWithDefaults
from .models import Message


class MessageForm(forms.ModelForm):
    """
    Form for composing and sending a message, either to an existing chat or to start a new chat with another entity.
    """

    class Meta:
        model = Message
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        """
        Initializes the form, extracting the from_entity and either a to_entity or a chat keyword argument (exactly one of them must be given), and sets up the form helper with the correct submit action.

        :param args: Positional arguments passed to the parent form.
        :param kwargs: Keyword arguments, including from_entity, and either to_entity or chat.
        :raises AssertionError: If both or neither of to_entity/chat are provided together with from_entity.
        """
        self.from_entity = kwargs.pop('from_entity', None)
        self.to_entity = kwargs.pop('to_entity', None)
        self.chat = kwargs.pop('chat', None)
        assert bool(self.from_entity and self.to_entity) != bool(self.from_entity and self.chat)
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        if (self.chat):
            self.helper.form_action = reverse(viewname='messages:chat_send', kwargs={'chat_slug': self.chat.get_slug(current_user=self.from_entity)})
        else:
            self.helper.form_action = reverse(viewname='messages_entity:user_send', kwargs={'slug': self.to_entity.slug})
        self.helper.form_class = 'form-vertical'
        self.helper.layout = Layout(
            InlineField('text', style="height: 55px", onblur='this.value = this.value.trim();'),
            Submit('submit', pgettext_lazy(context=self.from_entity.get_gender(), message='Send')),
        )

    def save(self, commit=True):
        """
        Saves the form by sending the message to the target chat or entity. Only supports commit=True.

        :param commit: Must be True; this form does not support deferred saving.
        :type commit: bool
        :return: The newly created message.
        :rtype: speedy.core.messages.models.Message
        """
        assert commit
        return Message.objects.send_message(from_entity=self.from_entity, to_entity=self.to_entity, chat=self.chat, text=self.cleaned_data['text'])


