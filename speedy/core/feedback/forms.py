from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Row
from django.utils.translation import ugettext_lazy as _

from speedy.core.accounts_core.forms import ModelFormWithDefaults
from .models import Feedback


class FeedbackForm(ModelFormWithDefaults):
    class Meta:
        model = Feedback
        fields = ('sender_name', 'sender_email', 'text')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.helper = FormHelper()
        if self.defaults.get('sender'):
            del self.fields['sender_name']
            del self.fields['sender_email']
        else:
            self.fields['sender_name'].required = True
            self.fields['sender_email'].required = True
            self.helper.add_layout(Row(
                Div('sender_name', css_class='col-md-6'),
                Div('sender_email', css_class='col-md-6'),
            ))
        self.helper.add_input(Submit('submit', _('Send')))
