from crispy_forms.layout import Submit, Div, Row

from django import forms
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError

from speedy.core.base.forms import ModelFormWithDefaults, FormHelperWithDefaults
from .models import Feedback


class FeedbackForm(ModelFormWithDefaults):
    _not_allowed_strings = ["monkeydigital.co@gmail.com", "https://monkeydigital.co/", "support@monkeydigital.co", "https://www.monkeydigital.co/", "https://googlealexarank.com/", "noreplygooglealexarank@gmail.com", "http://www.hirelabas.nl/", "manager@hirelabas.nl", "infomatinj@gmail.com", "eric@talkwithcustomer.com", "http://www.talkwithcustomer.com"]
    no_bots = forms.CharField(label=_('Type the number "17"'), required=True)

    class Meta:
        model = Feedback
        fields = ('sender_name', 'sender_email', 'text', 'no_bots')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        if (self.defaults.get('sender')):
            del self.fields['sender_name']
            del self.fields['sender_email']
            del self.fields['no_bots']
            self.helper.add_input(Submit('submit', pgettext_lazy(context=self.defaults['sender'].get_gender(), message='Send')))
        else:
            self.fields['sender_name'].required = True
            self.fields['sender_email'].required = True
            self.helper.add_layout(Row(
                Div('sender_name', css_class='col-md-6'),
                Div('sender_email', css_class='col-md-6'),
            ))
            self.helper.add_input(Submit('submit', _('Send')))

    def clean_text(self):
        text = self.cleaned_data.get('text')
        for not_allowed_string in self._not_allowed_strings:
            if (not_allowed_string in text):
                raise ValidationError(_("Please contact us by e-mail."))
        return text

    def clean_no_bots(self):
        no_bots = self.cleaned_data.get('no_bots')
        if (not (no_bots == "17")):
            raise ValidationError(_("Not 17."))
        return no_bots


