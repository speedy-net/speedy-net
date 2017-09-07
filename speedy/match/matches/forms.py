import math
from itertools import zip_longest

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Row, Submit, Field
from django.utils.translation import pgettext_lazy

from speedy.match.accounts.forms import SpeedyMatchProfileActivationForm


class MatchSettingsMiniForm(SpeedyMatchProfileActivationForm):
    def get_fields(self):
        return ('diet_match', 'min_age_match', 'max_age_match')


class MatchSettingsFullForm(SpeedyMatchProfileActivationForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.helper = FormHelper()
        # split into two columns
        field_names = list(self.fields.keys())
        custom_field_names = ('gender_to_match', 'diet_match', 'smoking_match', 'marital_status_match')
        self.helper.add_layout(Div(*[
            Row(*[
                # a little hack that forces display of custom widgets
                Div(Field(field, template='%s/render.html') if field in custom_field_names else field,
                    css_class='col-md-6')
                for field in pair])
            for pair in zip_longest(field_names[::2], field_names[1::2])
        ]))
        self.helper.add_input(
            Submit('submit', pgettext_lazy(context=self.instance.user.get_gender(), message='Save Changes')))

    def get_fields(self):
        return ('gender_to_match', 'match_description', 'min_age_match', 'max_age_match', 'diet_match', 'smoking_match',
                'marital_status_match')


class AboutMeForm(MatchSettingsFullForm):
    def get_fields(self):
        return (
        'profile_description', 'city', 'height', 'children', 'more_children', 'diet', 'smoking', 'marital_status')
