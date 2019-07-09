import json

from django import forms
from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from speedy.core.base.utils import to_attribute
from speedy.core.uploads.models import Image
from speedy.core.accounts.models import User
from speedy.core.accounts.forms import ProfileNotificationsForm as CoreProfileNotificationsForm

from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from speedy.match.accounts import validators as speedy_match_accounts_validators, utils


class CustomPhotoWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return render_to_string(template_name='accounts/edit_profile/activation_form/photo_widget.html', context={
            'name': name,
            'user_photo': self.attrs['user'].photo,
        })


class CustomJsonWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        return render_to_string(template_name='accounts/edit_profile/activation_form/json_widget.html', context={'choices': self.choices, 'name': name, 'value': json.loads(value)})

    def value_from_datadict(self, data, files, name):
        return data.get(name)


class SpeedyMatchProfileBaseForm(forms.ModelForm):
    validators = {
        'height': [speedy_match_accounts_validators.validate_height],
        'smoking_status': [speedy_match_accounts_validators.validate_smoking_status],
        'marital_status': [speedy_match_accounts_validators.validate_marital_status],
        **{to_attribute(name='profile_description', language_code=language_code): [speedy_match_accounts_validators.validate_profile_description] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='city', language_code=language_code): [speedy_match_accounts_validators.validate_city] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='children', language_code=language_code): [speedy_match_accounts_validators.validate_children] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='more_children', language_code=language_code): [speedy_match_accounts_validators.validate_more_children] for language_code, language_name in django_settings.LANGUAGES},
        **{to_attribute(name='match_description', language_code=language_code): [speedy_match_accounts_validators.validate_match_description] for language_code, language_name in django_settings.LANGUAGES},
        'gender_to_match': [speedy_match_accounts_validators.validate_gender_to_match],
        'min_age_match': [speedy_match_accounts_validators.validate_min_age_match],
        'max_age_match': [speedy_match_accounts_validators.validate_max_age_match],
        'diet_match': [speedy_match_accounts_validators.validate_diet_match],
        'smoking_status_match': [speedy_match_accounts_validators.validate_smoking_status_match],
        'marital_status_match': [speedy_match_accounts_validators.validate_marital_status_match],
    }
    # ~~~~ TODO: diet choices depend on the current user's gender. Also same for smoking status and marital status.
    diet = forms.ChoiceField(choices=User.DIET_VALID_CHOICES, widget=forms.RadioSelect(), label=_('My diet'), validators=[speedy_match_accounts_validators.validate_diet])
    photo = forms.ImageField(required=False, widget=CustomPhotoWidget, label=_('Add profile picture'))

    class Meta:
        model = SpeedyMatchSiteProfile
        fields = (
            'photo',
            *(to_attribute(name='profile_description', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            *(to_attribute(name='city', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            'height',
            *(to_attribute(name='children', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            *(to_attribute(name='more_children', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            'diet',
            'smoking_status',
            'marital_status',
            'gender_to_match',
            *(to_attribute(name='match_description', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
            'min_age_match',
            'max_age_match',
            'diet_match',
            'smoking_status_match',
            'marital_status_match',
        )
        widgets = {
            'smoking_status': forms.RadioSelect(),
            'marital_status': forms.RadioSelect(),
            **{to_attribute(name='profile_description', language_code=language_code): forms.Textarea(attrs={'rows': 3, 'cols': 25}) for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='city', language_code=language_code): forms.TextInput() for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='children', language_code=language_code): forms.TextInput() for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='more_children', language_code=language_code): forms.TextInput() for language_code, language_name in django_settings.LANGUAGES},
            **{to_attribute(name='match_description', language_code=language_code): forms.Textarea(attrs={'rows': 3, 'cols': 25}) for language_code, language_name in django_settings.LANGUAGES},
            'diet_match': CustomJsonWidget(choices=User.DIET_VALID_CHOICES),
            'smoking_status_match': CustomJsonWidget(choices=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_CHOICES),
            'marital_status_match': CustomJsonWidget(choices=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        raise Exception("def __init__ line 87")
        self.step = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
        fields = self.get_fields()
        # print(fields) # ~~~~ TODO: remove this line!
        fields_for_deletion = set(self.fields.keys()) - set(fields)
        for field_for_deletion in fields_for_deletion:
            del self.fields[field_for_deletion]
        if ('gender_to_match' in self.fields):
            self.fields['gender_to_match'] = forms.MultipleChoiceField(choices=User.GENDER_CHOICES, widget=forms.CheckboxSelectMultiple)
        if ('photo' in self.fields):
            self.fields['photo'].widget.attrs['user'] = self.instance.user
        if ('diet' in self.fields):
            raise Exception
            self.fields['diet'].widget.choices = self.instance.user.get_diet_choices()
            self.fields['diet'].initial = self.instance.user.diet # ~~~~ TODO: diet, smoking_status and marital_status - this line is required if the field is in class User - not in class SpeedyMatchSiteProfile.
        if ('smoking_status' in self.fields):
            raise Exception
            self.fields['smoking_status'].widget.choices = self.instance.get_smoking_status_choices()
        if ('marital_status' in self.fields):
            raise Exception
            self.fields['marital_status'].widget.choices = self.instance.get_marital_status_choices()
        # ~~~~ TODO: diet match choices gender is the desired match gender - either male, female or other. If more than one gender option is selected, then other. Same is for smoking status and marital status.
        if ('diet_match' in self.fields):
            self.fields['diet_match'].widget.choices = self.instance.get_diet_match_choices()
        if ('smoking_status_match' in self.fields):
            self.fields['smoking_status_match'].widget.choices = self.instance.get_smoking_status_match_choices()
        if ('marital_status_match' in self.fields):
            self.fields['marital_status_match'].widget.choices = self.instance.get_marital_status_match_choices()
        for field_name, field in self.fields.items():
            if (field_name in self.validators):
                field.validators.extend(self.validators[field_name])
                field.required = True

    def clean_photo(self):
        photo = self.files.get('photo')
        if (not (photo)):
            photo = self.instance.user.photo
        speedy_match_accounts_validators.validate_photo(photo=photo)
        return self.cleaned_data

    def clean_gender_to_match(self):
        return [int(value) for value in self.cleaned_data['gender_to_match']]

    def clean(self):
        if (('min_age_match' in self.fields) and ('max_age_match' in self.fields)):
            min_age_match = self.cleaned_data.get('min_age_match')
            max_age_match = self.cleaned_data.get('max_age_match')
            speedy_match_accounts_validators.validate_min_max_age_to_match(min_age_match=min_age_match, max_age_match=max_age_match)
        return self.cleaned_data

    def save(self, commit=True):
        if ((commit) and ('photo' in self.fields)):
            if (self.files):
                user_image = Image(owner=self.instance.user, file=self.files['photo'])
                user_image.save()
                self.instance.user.photo = user_image
            self.instance.user.save()
        if ((commit) and ('diet' in self.fields)):
            self.instance.user.diet = self.cleaned_data['diet']
            self.instance.user.save()
        super().save(commit=commit)
        if (commit):
            activation_step = self.instance.activation_step
            step, errors = self.instance.validate_profile_and_activate()
            self.instance.activation_step = min(activation_step + 1, step)
            if (self.instance.activation_step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS) - 1):
                self.instance.activation_step = len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
            self.instance.save(update_fields={to_attribute('activation_step')})
        return self.instance

    def get_fields(self):
        # This function is not defined in this base (abstract) form.
        raise NotImplementedError()


class SpeedyMatchProfileActivationForm(SpeedyMatchProfileBaseForm):
    def get_fields(self):
        return utils.get_step_form_fields(step=self.step)


class ProfileNotificationsForm(CoreProfileNotificationsForm):
    _profile_fields = ("notify_on_like",)


