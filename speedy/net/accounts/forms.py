from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from django.utils.translation import ugettext_lazy as _

from .models import SiteProfile


class ProfilePrivacyForm(forms.ModelForm):
    class Meta:
        model = SiteProfile
        fields = ('access_dob_day_month', 'access_dob_year')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Save Changes')))
