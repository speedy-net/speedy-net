from crispy_forms.layout import Div, Row, HTML, Field

from django.utils.translation import pgettext_lazy

from speedy.core.base.utils import to_attribute
from speedy.core.base.forms import FormHelperWithDefaults
from speedy.match.accounts.forms import SpeedyMatchProfileBaseForm


class SpeedyMatchSettingsMiniForm(SpeedyMatchProfileBaseForm):
    """
    Compact matching-preferences form shown inline (e.g. in the sidebar), exposing only the most important match fields.

    Methods:
        get_fields(self): Returns the field names included in this form.
        get_visible_fields(self): Returns the field names visible on this form.
    """
    def get_fields(self):
        """
        Returns the field names included in this form.

        :return: A tuple of field names.
        :rtype: tuple
        """
        return ('gender_to_match', to_attribute(name='match_description'), 'min_age_to_match', 'max_age_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match')

    def get_visible_fields(self):
        """
        Returns the field names visible on this form.

        :return: A tuple of visible field names.
        :rtype: tuple
        """
        return ('diet_match', 'min_age_to_match', 'max_age_to_match')


class SpeedyMatchProfileFullSettingsBaseForm(SpeedyMatchProfileBaseForm):
    """
    Base form for the full-page Speedy Match settings forms, laying out fields in two-column rows and adding a save button.

    Methods:
        __init__(self, *args, **kwargs): Builds the form and its crispy-forms layout.
        get_field_pairs(self): Not implemented in this abstract base form; must be implemented by subclasses.
    """
    def __init__(self, *args, **kwargs):
        """
        Builds the form, then constructs its two-column crispy-forms layout and appends a save button.

        :param args: Positional arguments passed to the parent form.
        :param kwargs: Keyword arguments passed to the parent form.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        self.helper.error_text_inline = False
        # split into two columns
        custom_field_names = ('gender_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match')
        self.helper.add_layout(
            Div(*[
                Row(*[
                    # A little hack that forces display of custom widgets
                    Div(Field(field, template='%s/speedy_match_custom_field.html') if (field in custom_field_names) else field, css_class='col-md-6')
                    for field in pair
                ])
                for pair in self.get_field_pairs()
            ]),
        )
        self.helper.layout.append(
            HTML('<button type="submit" title="{button_text}" class="btn btn-primary"><i class="fas fa-save"></i><span class="label ml-2">{button_text}</span></button>'.format(
                button_text=pgettext_lazy(context=self.instance.user.get_gender(), message='Save Changes'),
            )),
        )

    def get_field_pairs(self):
        """
        Returns the field pairs used to lay out this form in two-column rows.

        :return: A tuple of field-name pairs/tuples.
        :rtype: tuple
        :raises NotImplementedError: Always, as this is an abstract base form.
        """
        # This method is not defined in this base (abstract) form.
        raise NotImplementedError("This method is not defined in this base (abstract) form.")


class SpeedyMatchProfileFullMatchForm(SpeedyMatchProfileFullSettingsBaseForm):
    """
    Full-page form for editing a user's matching preferences (gender to match, age range, match description, diet/smoking/relationship match ranks).

    Methods:
        get_fields(self): Returns the field names included in this form.
        get_field_pairs(self): Returns the field pairs used to lay out this form.
        get_visible_fields(self): Returns the field names visible on this form.
    """
    def get_fields(self):
        """
        Returns the field names included in this form.

        :return: A tuple of field names.
        :rtype: tuple
        """
        return ('gender_to_match', to_attribute(name='match_description'), 'min_age_to_match', 'max_age_to_match', 'diet_match', 'smoking_status_match', 'relationship_status_match')

    def get_field_pairs(self):
        """
        Returns the field pairs used to lay out this form in two-column rows.

        :return: A tuple of field-name pairs/tuples.
        :rtype: tuple
        """
        return (('gender_to_match', to_attribute(name='match_description')), ('min_age_to_match', 'max_age_to_match'), ('diet_match', 'smoking_status_match'), ('relationship_status_match',))

    def get_visible_fields(self):
        """
        Returns the field names visible on this form.

        :return: The field names included in this form.
        :rtype: tuple
        """
        return self.get_fields()


class SpeedyMatchProfileFullAboutMeForm(SpeedyMatchProfileFullSettingsBaseForm):
    """
    Full-page form for editing a user's "about me" profile fields (description, city, height, children, lifestyle choices).

    Methods:
        get_fields(self): Returns the field names included in this form.
        get_field_pairs(self): Returns the field pairs used to lay out this form.
        get_visible_fields(self): Returns the field names visible on this form.
    """
    def get_fields(self):
        """
        Returns the field names included in this form.

        :return: A tuple of field names.
        :rtype: tuple
        """
        return (to_attribute(name='profile_description'), to_attribute(name='city'), 'height', to_attribute(name='children'), to_attribute(name='more_children'), 'diet', 'smoking_status', 'relationship_status')

    def get_field_pairs(self):
        """
        Returns the field pairs used to lay out this form in two-column rows.

        :return: A tuple of field-name pairs/tuples.
        :rtype: tuple
        """
        return ((to_attribute(name='profile_description'),), (to_attribute(name='city'), 'height'), (to_attribute(name='children'), to_attribute(name='more_children')), ('diet', 'smoking_status'), ('relationship_status',))

    def get_visible_fields(self):
        """
        Returns the field names visible on this form.

        :return: The field names included in this form.
        :rtype: tuple
        """
        return self.get_fields()


