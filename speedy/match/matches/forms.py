from itertools import zip_longest

from crispy_forms.layout import Div, Row, Submit, Field
from django.utils.translation import pgettext_lazy

from speedy.core.base.utils import to_attribute
from speedy.core.base.forms import FormHelperWithDefaults
from speedy.match.accounts.forms import SpeedyMatchProfileBaseForm


class SpeedyMatchSettingsMiniForm(SpeedyMatchProfileBaseForm):
    def get_fields(self):
        return ('gender_to_match', to_attribute(name='match_description'), 'min_age_to_match', 'max_age_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match')

    def get_visible_fields(self):
        return ('diet_match', 'min_age_to_match', 'max_age_to_match')


class SpeedyMatchProfileFullSettingsBaseForm(SpeedyMatchProfileBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        # split into two columns
        custom_field_names = ('gender_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match')
        self.helper.add_layout(Div(*[
            Row(*[
                # a little hack that forces display of custom widgets
                Div(Field(field, template='%s/speedy_match_custom_field.html') if (field in custom_field_names) else field, css_class='col-md-6')
                for field in pair
            ])
            for pair in self.get_field_pairs()
        ]))
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.user.get_gender(), message='Save Changes')))

    def get_field_pairs(self):
        # This function is not defined in this base (abstract) form.
        raise NotImplementedError()


class SpeedyMatchProfileFullMatchForm(SpeedyMatchProfileFullSettingsBaseForm):
    def get_fields(self):
        return ('gender_to_match', to_attribute(name='match_description'), 'min_age_to_match', 'max_age_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match')

    def get_field_pairs(self):
        return (('gender_to_match', to_attribute(name='match_description')), ('min_age_to_match', 'max_age_to_match'), ('diet_match', 'smoking_status_match'), ('relationship_status_match', ))

    def get_visible_fields(self):
        return self.get_fields()


class SpeedyMatchProfileFullAboutMeForm(SpeedyMatchProfileFullSettingsBaseForm):
    def get_fields(self):
        return (to_attribute(name='profile_description'), to_attribute(name='city'), 'height', to_attribute(name='children'), to_attribute(name='more_children'), 'diet', 'smoking_status', 'relationship_status')

    def get_field_pairs(self):
        return ((to_attribute(name='profile_description'), ), (to_attribute(name='city'), 'height'), (to_attribute(name='children'), to_attribute(name='more_children')), ('diet', 'smoking_status'), ('relationship_status', ))

    def get_visible_fields(self):
        return self.get_fields()


