from crispy_forms.layout import Submit, Div, Row, MultiWidgetField

from django import forms
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError

from speedy.core.base.forms import ModelFormWithDefaults, FormHelperWithDefaults
from speedy.core.accounts.forms import AddAttributesToFieldsMixin
from .models import Feedback


class FeedbackForm(AddAttributesToFieldsMixin, ModelFormWithDefaults):
    """
    Form used to submit feedback, abuse reports (on an entity or a file), and anti-spam validation.

    Attributes:
        _not_allowed_strings (list): Strings that are not allowed to appear in the feedback text (likely spam links).
        no_bots (CharField): Anti-bot field requiring the text "17" to be entered.

    Methods:
        __init__(self, *args, **kwargs): Removes sender-identifying and anti-bot fields and sets the submit button text when a logged-in sender is provided; otherwise requires the sender's name and email.
        clean_text(self): Validates that the feedback text doesn't contain any not-allowed strings.
        clean_no_bots(self): Validates that the anti-bot field contains the value "17".
    """
    _not_allowed_strings = ["https://t.me/pump_upp", "https://datebest.net", "https://t.me/FeedbackFormEU"]
    no_bots = forms.CharField(label=_('Type the number "17"'), required=True)

    class Meta:
        model = Feedback
        fields = ('sender_name', 'sender_email', 'text', 'no_bots')

    def __init__(self, *args, **kwargs):
        """
        Initializes the form; if a logged-in sender is provided in defaults, removes the sender name/email and anti-bot fields and sets the submit button text (gender-aware); otherwise requires the sender's name and email fields and adds the anti-bot layout.

        :param args: Positional arguments passed to the parent implementation.
        :param kwargs: Keyword arguments passed to the parent implementation.
        """
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
            self.helper.add_layout(
                MultiWidgetField(
                    Row(
                        Div('sender_name', css_class='col-md-6'),
                        Div('sender_email', css_class='col-md-6'),
                    ),
                    'text',
                    'no_bots',
                ),
            )
            self.helper.add_input(Submit('submit', _('Send')))

    def clean_text(self):
        """
        Validates that the feedback text doesn't contain any of the not-allowed (spam-related) strings.

        :return: The cleaned text.
        :rtype: str
        :raises ValidationError: If the text contains a not-allowed string.
        """
        text = self.cleaned_data.get('text')
        for not_allowed_string in self._not_allowed_strings:
            if (not_allowed_string in text):
                raise ValidationError(_("Please contact us by email."))
        return text

    def clean_no_bots(self):
        """
        Validates that the anti-bot field contains the value "17".

        :return: The cleaned anti-bot field value.
        :rtype: str
        :raises ValidationError: If the value is not "17".
        """
        no_bots = self.cleaned_data.get('no_bots')
        if (not (no_bots == "17")):
            raise ValidationError(_("Not 17."))
        return no_bots


