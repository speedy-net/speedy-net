import json

from django import forms
from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from speedy.core.base.utils import to_attribute, update_form_field_choices
from speedy.core.base.forms import DeleteUnneededFieldsMixin
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


class SpeedyMatchProfileBaseForm(DeleteUnneededFieldsMixin, forms.ModelForm):
    user_fields = (
        'diet',
        'smoking_status',
        'marital_status',
        *(to_attribute(name='city', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES),
    )
    validators = {
        'height': [speedy_match_accounts_validators.validate_height],
        'diet': [speedy_match_accounts_validators.validate_diet],
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
    diet = forms.ChoiceField(choices=User.DIET_VALID_CHOICES, widget=forms.RadioSelect(), label=_('My diet'))
    smoking_status = forms.ChoiceField(choices=User.SMOKING_STATUS_VALID_CHOICES, widget=forms.RadioSelect(), label=_('My smoking status'))
    marital_status = forms.ChoiceField(choices=User.MARITAL_STATUS_VALID_CHOICES, widget=forms.RadioSelect(), label=_('My marital status'))
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
            'smoking_status_match': CustomJsonWidget(choices=User.SMOKING_STATUS_VALID_CHOICES),
            'marital_status_match': CustomJsonWidget(choices=User.MARITAL_STATUS_VALID_CHOICES),
        }

    @staticmethod
    def __new__(cls, *args, **kwargs):
        for language_code, language_name in django_settings.LANGUAGES:
            setattr(cls, to_attribute(name='city', language_code=language_code), forms.CharField(label=_('city or locality'), max_length=120))
        return super().__new__(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
        self.delete_unneeded_fields()
        if ('gender_to_match' in self.fields):
            self.fields['gender_to_match'] = forms.MultipleChoiceField(choices=User.GENDER_CHOICES, widget=forms.CheckboxSelectMultiple)
        if ('photo' in self.fields):
            self.fields['photo'].widget.attrs['user'] = self.instance.user
        if ('diet' in self.fields):
            update_form_field_choices(field=self.fields['diet'], choices=self.instance.user.get_diet_choices())
            self.fields['diet'].initial = self.instance.user.diet
        if ('smoking_status' in self.fields):
            update_form_field_choices(field=self.fields['smoking_status'], choices=self.instance.user.get_smoking_status_choices())
            self.fields['smoking_status'].initial = self.instance.user.smoking_status
        if ('marital_status' in self.fields):
            update_form_field_choices(field=self.fields['marital_status'], choices=self.instance.user.get_marital_status_choices())
            self.fields['marital_status'].initial = self.instance.user.marital_status
        if ('diet_match' in self.fields):
            update_form_field_choices(field=self.fields['diet_match'], choices=self.instance.get_diet_match_choices())
        if ('smoking_status_match' in self.fields):
            update_form_field_choices(field=self.fields['smoking_status_match'], choices=self.instance.get_smoking_status_match_choices())
        if ('marital_status_match' in self.fields):
            update_form_field_choices(field=self.fields['marital_status_match'], choices=self.instance.get_marital_status_match_choices())
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
        if (commit):
            if ('photo' in self.fields):
                if (self.files):
                    user_image = Image(owner=self.instance.user, file=self.files['photo'])
                    user_image.save()
                    self.instance.user.photo = user_image
            for field_name in self.user_fields:
                if (field_name in self.fields):
                    setattr(self.instance.user, field_name, self.cleaned_data[field_name])
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


