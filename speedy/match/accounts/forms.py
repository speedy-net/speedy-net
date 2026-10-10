"""
Forms of the Speedy Match accounts app: the profile and activation forms (including the custom checkbox widget) and the notifications form.
"""
import logging
import json

from django import forms
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _, pgettext_lazy
from django.contrib.sites.models import Site

from speedy.core.base.utils import to_attribute, update_form_field_choices
from speedy.core.base.forms import DeleteUnneededFieldsMixin
from speedy.core.uploads.models import Image
from speedy.core.accounts.models import User
from speedy.core.accounts import forms as speedy_core_accounts_forms, validators as speedy_core_accounts_validators
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from speedy.match.accounts import validators as speedy_match_accounts_validators, utils

logger = logging.getLogger(__name__)


class CustomJsonWidget(forms.CheckboxSelectMultiple):
    """
    Custom checkbox-select-multiple widget that renders and parses its value as JSON, used for the diet/smoking/relationship match rank fields.

    Methods:
        render(self, name, value, attrs=None, renderer=None): Renders the widget using the json_widget.html template.
        value_from_datadict(self, data, files, name): Extracts the raw value for this field from the submitted form data.
    """

    def render(self, name, value, attrs=None, renderer=None):
        """
        Renders the widget using the json_widget.html template, decoding the JSON-encoded value back into choice ranks.

        :param name: The field name.
        :type name: str
        :param value: The JSON-encoded field value.
        :type value: str
        :param attrs: Extra HTML attributes for the widget (unused).
        :param renderer: The form renderer (unused).
        :return: The rendered HTML for the widget.
        :rtype: str
        """
        return render_to_string(template_name='accounts/edit_profile/widgets/json_widget.html', context={'choices': self.choices, 'name': name, 'value': json.loads(value)})

    def value_from_datadict(self, data, files, name):
        """
        Extracts the raw (JSON-encoded) value for this field from the submitted form data.

        :param data: The submitted form data.
        :type data: dict
        :param files: The submitted files (unused).
        :param name: The field name.
        :type name: str
        :return: The raw JSON string value for this field.
        :rtype: str
        """
        return data.get(name)


class SpeedyMatchProfileBaseForm(DeleteUnneededFieldsMixin, forms.ModelForm):
    """
    Base form for editing a Speedy Match site profile, shared by the step-by-step activation form. Defines all profile fields, their validators, widgets and error messages, and handles saving changes back to both the User and SiteProfile models.

    Attributes:
        user_fields: Field names that belong to the User model rather than the SiteProfile model.
        validators: A mapping of field name to the list of validator functions to apply.
        profile_picture, diet, smoking_status, relationship_status, gender_to_match: Extra form fields not directly defined on the SiteProfile model.

    Methods:
        __init__(self, *args, **kwargs): Builds the form, creates dynamic fields, updates labels/choices/validators and rearranges fields.
        clean_profile_picture(self): Validates and processes an uploaded profile picture.
        clean_gender_to_match(self): Converts the submitted gender-to-match values to integers.
        clean(self): Performs cross-field validation of the minimal/maximal age to match.
        save(self, commit=True): Saves the form data to both the User and SiteProfile models, and advances the activation step.
        get_fields(self): Not implemented in this abstract base form; must be implemented by subclasses.
        get_visible_fields(self): Not implemented in this abstract base form; must be implemented by subclasses.
        get_hidden_fields(self): Returns the field names that are present but not visible.
    """
    # Fields from the User model.
    user_fields = (
        'diet',
        'smoking_status',
        'relationship_status',
        *(to_attribute(name='city', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
    )
    # Fields validators.
    validators = {
        'height': [speedy_match_accounts_validators.validate_height],
        'diet': [speedy_match_accounts_validators.validate_diet],
        'smoking_status': [speedy_match_accounts_validators.validate_smoking_status],
        'relationship_status': [speedy_match_accounts_validators.validate_relationship_status],
        **{to_attribute(name='profile_description', language_code=language_code): [speedy_match_accounts_validators.validate_profile_description] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='city', language_code=language_code): [speedy_match_accounts_validators.validate_city] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='children', language_code=language_code): [speedy_match_accounts_validators.validate_children] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='more_children', language_code=language_code): [speedy_match_accounts_validators.validate_more_children] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='match_description', language_code=language_code): [speedy_match_accounts_validators.validate_match_description] for language_code, language_name in django_settings.LANGUAGES},
        'gender_to_match': [speedy_match_accounts_validators.validate_gender_to_match],
        'min_age_to_match': [speedy_match_accounts_validators.validate_min_age_to_match],
        'max_age_to_match': [speedy_match_accounts_validators.validate_max_age_to_match],
        'diet_match': [speedy_match_accounts_validators.validate_diet_match],
        'smoking_status_match': [speedy_match_accounts_validators.validate_smoking_status_match],
        'relationship_status_match': [speedy_match_accounts_validators.validate_relationship_status_match],
    }
    # Fields who are not in the SpeedyMatchSiteProfile model.
    profile_picture = forms.ImageField(required=False, widget=speedy_core_accounts_forms.CustomPhotoWidget, label=_('Add profile picture'), error_messages={'required': _("A profile picture is required.")})
    diet = forms.ChoiceField(widget=forms.RadioSelect(), label=_('My diet'), error_messages={'required': _("Your diet is required.")}, required=True)
    smoking_status = forms.ChoiceField(widget=forms.RadioSelect(), label=_('My smoking status'), error_messages={'required': _("Your smoking status is required.")}, required=True)
    relationship_status = forms.ChoiceField(widget=forms.RadioSelect(), label=_('My relationship status'), error_messages={'required': _("Your relationship status is required.")}, required=True)
    gender_to_match = forms.MultipleChoiceField(choices=User.GENDER_CHOICES, widget=forms.CheckboxSelectMultiple, error_messages={'required': _("Gender to match is required.")}, required=True)

    class Meta:
        model = SpeedyMatchSiteProfile
        fields = (
            'profile_picture',
            *(to_attribute(name='profile_description', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            'height',
            *(to_attribute(name='children', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            *(to_attribute(name='more_children', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            'diet',
            'smoking_status',
            'relationship_status',
            'gender_to_match',
            *(to_attribute(name='match_description', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            'min_age_to_match',
            'max_age_to_match',
            'diet_match',
            'smoking_status_match',
            'relationship_status_match',
        )
        widgets = {
            'smoking_status': forms.RadioSelect(),
            'relationship_status': forms.RadioSelect(),
            **{to_attribute(name='profile_description', language_code=language_code): forms.Textarea(attrs={'rows': 6, 'cols': 40}) for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='city', language_code=language_code): forms.TextInput() for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='children', language_code=language_code): forms.TextInput() for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='more_children', language_code=language_code): forms.TextInput() for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='match_description', language_code=language_code): forms.Textarea(attrs={'rows': 6, 'cols': 40}) for language_code, language_name in django_settings.LANGUAGES},
            'diet_match': CustomJsonWidget(choices=User.DIET_VALID_CHOICES),
            'smoking_status_match': CustomJsonWidget(choices=User.SMOKING_STATUS_VALID_CHOICES),
            'relationship_status_match': CustomJsonWidget(choices=User.RELATIONSHIP_STATUS_VALID_CHOICES),
        }
        error_messages = {
            'profile_picture': {
                'required': _("A profile picture is required."),
            },
            'height': {
                'required': _("Your height is required."),
            },
            'diet': {
                'required': _("Your diet is required."),
            },
            'smoking_status': {
                'required': _("Your smoking status is required."),
            },
            'relationship_status': {
                'required': _("Your relationship status is required."),
            },
            **{to_attribute(name='profile_description', language_code=language_code): {
                'required': _("Please write a few words about yourself."),
            } for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='city', language_code=language_code): {
                'required': _("Please write where you live."),
            } for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='children', language_code=language_code): {
                'required': _("Do you have children? How many?"),
            } for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='more_children', language_code=language_code): {
                'required': _("Do you want (more) children?"),
            } for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='match_description', language_code=language_code): {
                'required': _("Who is your ideal partner?"),
            } for language_code, language_name in django_settings.LANGUAGES},
            'gender_to_match': {
                'required': _("Gender to match is required."),
            },
            'min_age_to_match': {
                'required': _("Minimal age to match is required."),
            },
            'max_age_to_match': {
                'required': _("Maximal age to match is required."),
            },
            'diet_match': {
                'required': _("Diet match is required."),
            },
            'smoking_status_match': {
                'required': _("Smoking status match is required."),
            },
            'relationship_status_match': {
                'required': _("Relationship status match is required."),
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Builds the form: pops the "step" kwarg, creates the dynamic localized city field, deletes unneeded fields, updates field labels/choices/error-messages/initial-values according to the user's gender and language, attaches validators, and rearranges the fields according to get_fields().

        :param args: Positional arguments passed to the parent ModelForm.
        :param kwargs: Keyword arguments passed to the parent ModelForm; may include "step".
        """
        self.step = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
        # Create the localized city field dynamically.
        self.fields[to_attribute(name='city')] = forms.CharField(label=_('Where do you live?'), max_length=120, error_messages={'required': _("Please write where you live.")}, required=True)
        # Delete unneeded fields from the form.
        self.delete_unneeded_fields()
        # Update fields attributes according to the user's gender and language.
        if ('profile_picture' in self.fields):
            self.fields['profile_picture'].widget.attrs['user'] = self.instance.user
            self.fields['profile_picture'].label = pgettext_lazy(context=self.instance.user.get_gender(), message='Add profile picture')
        if ('height' in self.fields):
            self.fields['height'].label = pgettext_lazy(context=self.instance.user.get_gender(), message='My height in centimeters')
        if ('diet' in self.fields):
            update_form_field_choices(field=self.fields['diet'], choices=self.instance.user.get_diet_choices_with_description())
        if ('smoking_status' in self.fields):
            update_form_field_choices(field=self.fields['smoking_status'], choices=self.instance.user.get_smoking_status_choices())
        if ('relationship_status' in self.fields):
            update_form_field_choices(field=self.fields['relationship_status'], choices=self.instance.user.get_relationship_status_choices())
        if ('diet_match' in self.fields):
            update_form_field_choices(field=self.fields['diet_match'], choices=self.instance.get_diet_match_choices())
        if ('smoking_status_match' in self.fields):
            update_form_field_choices(field=self.fields['smoking_status_match'], choices=self.instance.get_smoking_status_match_choices())
        if ('relationship_status_match' in self.fields):
            update_form_field_choices(field=self.fields['relationship_status_match'], choices=self.instance.get_relationship_status_match_choices())
        if (to_attribute(name='profile_description') in self.fields):
            self.fields[to_attribute(name='profile_description')].error_messages = {'required': pgettext_lazy(context=self.instance.user.get_gender(), message="Please write a few words about yourself.")}
        if (to_attribute(name='city') in self.fields):
            self.fields[to_attribute(name='city')].label = pgettext_lazy(context=self.instance.user.get_gender(), message='Where do you live?')
            self.fields[to_attribute(name='city')].error_messages = {'required': pgettext_lazy(context=self.instance.user.get_gender(), message="Please write where you live.")}
        if (to_attribute(name='children') in self.fields):
            self.fields[to_attribute(name='children')].label = pgettext_lazy(context=self.instance.user.get_gender(), message='Do you have children? How many?')
            self.fields[to_attribute(name='children')].error_messages = {'required': pgettext_lazy(context=self.instance.user.get_gender(), message="Do you have children? How many?")}
        if (to_attribute(name='more_children') in self.fields):
            self.fields[to_attribute(name='more_children')].label = pgettext_lazy(context=self.instance.user.get_gender(), message='Do you want (more) children?')
            self.fields[to_attribute(name='more_children')].error_messages = {'required': pgettext_lazy(context=self.instance.user.get_gender(), message="Do you want (more) children?")}
        if (to_attribute(name='match_description') in self.fields):
            self.fields[to_attribute(name='match_description')].label = pgettext_lazy(context=self.instance.get_match_gender(), message='My ideal match')
            self.fields[to_attribute(name='match_description')].error_messages = {'required': pgettext_lazy(context=self.instance.get_match_gender(), message="Who is your ideal partner?")}
        if ('gender_to_match' in self.fields):
            self.fields['gender_to_match'].label = _('Gender to match')
        if ('min_age_to_match' in self.fields):
            self.fields['min_age_to_match'].label = pgettext_lazy(context=self.instance.get_match_gender(), message='Minimal age to match')
        if ('max_age_to_match' in self.fields):
            self.fields['max_age_to_match'].label = pgettext_lazy(context=self.instance.get_match_gender(), message='Maximal age to match')
        # Update the initial value of fields from the User model.
        for field_name in self.user_fields:
            if (field_name in self.fields):
                self.fields[field_name].initial = getattr(self.instance.user, field_name)
        # Update the fields validators.
        for field_name, field in self.fields.items():
            if (field_name in self.validators):
                field.validators.extend(self.validators[field_name])
                field.required = True
        # Rearrange the fields.
        self.order_fields(field_order=self.get_fields())

    def clean_profile_picture(self):
        """
        Validates the uploaded profile picture (or, if none was uploaded, the user's existing photo), creating and validating a temporary Image for a new upload and deleting it again if validation fails.

        :return: The cleaned profile_picture value.
        :raises ValidationError: If the profile picture is invalid.
        """
        profile_picture = self.files.get('profile_picture')
        if (profile_picture):
            user_image = Image(owner=self.instance.user, file=profile_picture)
            user_image.save()
            self.instance.user._new_profile_picture = user_image
            try:
                speedy_core_accounts_validators.validate_image_file_extension(value=profile_picture)
                speedy_core_accounts_validators.validate_profile_picture_for_user(user=self.instance.user, profile_picture=profile_picture, test_new_profile_picture=True)
            except ValidationError:
                user_image.file.delete(save=False)
                user_image.delete()
                raise
        else:
            profile_picture = self.instance.user.photo
            speedy_core_accounts_validators.validate_profile_picture_for_user(user=self.instance.user, profile_picture=profile_picture, test_new_profile_picture=False)
        return self.cleaned_data.get('profile_picture')

    def clean_gender_to_match(self):
        """
        Converts the submitted gender_to_match values (strings) to integers.

        :return: The genders to match, as a list of integers.
        :rtype: list of int
        """
        return [int(value) for value in self.cleaned_data['gender_to_match']]

    def clean(self):
        """
        Performs cross-field validation of the minimal/maximal age to match, when both fields are present on the form.

        :return: The cleaned data dictionary.
        :rtype: dict
        :raises ValidationError: If the minimal age to match is greater than the maximal age to match.
        """
        if (('min_age_to_match' in self.fields) and ('max_age_to_match' in self.fields)):
            min_age_to_match = self.cleaned_data.get('min_age_to_match')
            max_age_to_match = self.cleaned_data.get('max_age_to_match')
            speedy_match_accounts_validators.validate_min_max_age_to_match(min_age_to_match=min_age_to_match, max_age_to_match=max_age_to_match)
        return self.cleaned_data

    def save(self, commit=True):
        """
        Saves the form data to both the User and SiteProfile models, logs a height change if it occurred, applies a new profile picture if uploaded, enforces the minimal/maximal matchable height, and advances (or keeps) the profile's activation step, activating the profile once all steps are complete.

        :param commit: Whether to save the changes to the database.
        :type commit: bool
        :return: The saved SiteProfile instance.
        """
        if (commit):
            user_profile = SpeedyMatchSiteProfile.objects.get(pk=self.instance.pk)
            if (not (self.instance.height == user_profile.height)):
                site = Site.objects.get_current()
                language_code = get_language()
                if (user_profile.height is None):
                    logger_level = logger.debug
                else:
                    logger_level = logger.info
                logger_level('User changed height on {site_name}, user={user}, new height={new_height}, old height={old_height} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                    site_name=_(site.name),
                    user=self.instance.user,
                    new_height=self.instance.height,
                    old_height=user_profile.height,
                    registered_days_ago=(now() - self.instance.user.date_created).days,
                    language_code=language_code,
                ))
            if ('profile_picture' in self.fields):
                profile_picture = self.files.get('profile_picture')
                if (profile_picture):
                    self.instance.user.photo = self.instance.user._new_profile_picture
                    self.instance.profile_picture_months_offset = 5
            for field_name in self.user_fields:
                if (field_name in self.fields):
                    setattr(self.instance.user, field_name, self.cleaned_data[field_name])
            self.instance.user.save()
        super().save(commit=commit)
        if (commit):
            if (not (self.instance.not_allowed_to_use_speedy_match)):
                if (self.instance.activation_step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS) - 1):
                    if (not (SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH <= self.instance.height <= SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH)):
                        self.instance.not_allowed_to_use_speedy_match = True
                        self.instance.save()
                        logger.warning('User {user} is not allowed to use Speedy Match (height={height} (registered {registered_days_ago} days ago).'.format(
                            user=self.instance.user,
                            height=self.instance.height,
                            registered_days_ago=(now() - self.instance.user.date_created).days,
                        ))
            activation_step = self.instance.activation_step
            step, errors = self.instance.validate_profile_and_activate(commit=False)
            if (self.step == activation_step):
                self.instance.activation_step = min(activation_step + 1, step)
            else:
                self.instance.activation_step = min(activation_step, step)
            if (self.instance.activation_step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)):
                self.instance.activation_step = len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
                self.instance.validate_profile_and_activate(commit=True)
            self.instance.save()
        return self.instance

    def get_fields(self):
        """
        Returns the field names for this form.

        :raises NotImplementedError: Always, since this base (abstract) form doesn't define its fields.
        """
        # This method is not defined in this base (abstract) form.
        raise NotImplementedError("This method is not defined in this base (abstract) form.")

    def get_visible_fields(self):
        """
        Returns the visible field names for this form.

        :raises NotImplementedError: Always, since this base (abstract) form doesn't define its visible fields.
        """
        # This method is not defined in this base (abstract) form.
        raise NotImplementedError("This method is not defined in this base (abstract) form.")

    def get_hidden_fields(self):
        """
        Returns the field names that are present on the form but not visible (i.e. in get_fields() but not get_visible_fields()).

        :return: A generator of hidden field names.
        :rtype: generator of str
        """
        fields = self.get_fields()
        visible_fields = self.get_visible_fields()
        return (field_name for field_name in fields if (not (field_name in visible_fields)))


class SpeedyMatchProfileActivationForm(SpeedyMatchProfileBaseForm):
    """
    Form used for the step-by-step Speedy Match profile activation wizard, restricting fields to those relevant to the current step.

    Methods:
        get_fields(self): Returns the field names for the current activation step.
        get_visible_fields(self): Returns the visible field names, same as get_fields for this form.
    """

    def get_fields(self):
        """
        Returns the field names for the current activation step.

        :return: The field names relevant to the current step.
        :rtype: list of str
        """
        return utils.get_step_form_fields(step=self.step)

    def get_visible_fields(self):
        """
        Returns the visible field names, same as get_fields() for this form.

        :return: The visible field names.
        :rtype: list of str
        """
        return self.get_fields()


class ProfileNotificationsForm(speedy_core_accounts_forms.ProfileNotificationsForm):
    """
    Speedy Match notifications preferences form, restricted to the "notify on like" profile field.
    """
    _profile_fields = ("notify_on_like",)


