import json

from django import forms
from django.conf import settings

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from modeltranslation.forms import TranslationModelForm

from speedy.core.uploads.models import Image
from speedy.core.accounts.models import User
from speedy.core.accounts.forms import ProfileNotificationsForm as CoreProfileNotificationsForm

from .models import SiteProfile as SpeedyMatchSiteProfile
from speedy.match.accounts import validators


class CustomPhotoWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return render_to_string(template_name='accounts/edit_profile/activation_form/photo_widget.html', context={
            'name': name,
            'user_photo': self.attrs['user'].photo,
        })


class CustomJsonWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        return render_to_string(template_name='accounts/edit_profile/activation_form/json_widget.html', context={'choices': self.choices, 'name': name,'value': json.loads(value)})

    def value_from_datadict(self, data, files, name):
        return data.get(name)


class SpeedyMatchProfileActivationForm(TranslationModelForm):
    _validators = {
        'height': [validators.validate_height],
        'min_age_match': [validators.validate_min_age_match],
        'max_age_match': [validators.validate_max_age_match],
        'smoking_status': [validators.validate_smoking_status],
        'city': [validators.validate_city],
        'marital_status': [validators.validate_marital_status],
        'children': [validators.validate_children],
        'more_children': [validators.validate_more_children],
        'profile_description': [validators.validate_profile_description],
        'match_description': [validators.validate_match_description],
        'gender_to_match': [validators.validate_gender_to_match],
        'diet_match': [validators.validate_diet_match],
        'smoking_status_match': [validators.validate_smoking_status_match],
        'marital_status_match': [validators.validate_marital_status_match],
    }
    # ~~~~ TODO: diet choices depend on the current user's gender. Also same for smoking status and marital status.
    # diet = forms.ChoiceField(choices=User.DIET_VALID_CHOICES, widget=forms.RadioSelect(), label=_('My diet'), validators=[validators.validate_diet])
    diet = forms.ChoiceField(choices=User.DIET_CHOICES_WITH_DEFAULT, widget=forms.RadioSelect(), label=_('My diet'), validators=[validators.validate_diet]) #### TODO
    photo = forms.ImageField(required=False, widget=CustomPhotoWidget, label=_('Add profile picture'))

    class Meta:
        model = SpeedyMatchSiteProfile
        fields = ('photo', 'profile_description', 'city', 'height', 'children', 'more_children', 'diet',
                  'smoking_status', 'marital_status', 'gender_to_match', 'match_description', 'min_age_match', 'max_age_match', 'diet_match', 'smoking_status_match', 'marital_status_match')
        widgets = {
            'profile_description': forms.Textarea(attrs={'rows': 3, 'cols': 25}),
            'children': forms.TextInput(),
            'more_children': forms.TextInput(),
            'smoking_status': forms.RadioSelect(),
            'marital_status': forms.RadioSelect(),
            'match_description': forms.Textarea(attrs={'rows': 3, 'cols': 25}),
            # 'diet_match': CustomJsonWidget(choices=User.DIET_VALID_CHOICES),
            # 'smoking_status_match': CustomJsonWidget(choices=SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_CHOICES),
            # 'marital_status_match': CustomJsonWidget(choices=SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_CHOICES),
            'diet_match': CustomJsonWidget(choices=User.DIET_CHOICES_WITH_DEFAULT), #### TODO
            'smoking_status_match': CustomJsonWidget(choices=SpeedyMatchSiteProfile.SMOKING_STATUS_CHOICES_WITH_DEFAULT), #### TODO
            'marital_status_match': CustomJsonWidget(choices=SpeedyMatchSiteProfile.MARITAL_STATUS_CHOICES_WITH_DEFAULT), #### TODO
        }

    def clean_photo(self):
        photo = self.files.get('photo')
        if not photo:
            photo = self.instance.user.photo
        validators.validate_photo(photo=photo)
        return self.cleaned_data

    def clean_gender_to_match(self):
        return [int(value) for value in self.cleaned_data['gender_to_match']]

    def get_fields(self):
        return settings.SITE_PROFILE_FORM_FIELDS[self.step]

    def clean(self):
        if (('min_age_match' in self.fields) and ('max_age_match' in self.fields)):
            min_age_match = self.cleaned_data.get('min_age_match')
            max_age_match = self.cleaned_data.get('max_age_match')
            validators.validate_min_max_age_to_match(min_age_match=min_age_match, max_age_match=max_age_match)
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
        fields = self.get_fields()
        fields_for_deletion = set(self.fields.keys()) - set(fields)
        for field_for_deletion in fields_for_deletion:
            del self.fields[field_for_deletion]
        if ('gender_to_match' in self.fields):
            self.fields['gender_to_match'] = forms.MultipleChoiceField(choices=User.GENDER_CHOICES, widget=forms.CheckboxSelectMultiple)
        if ('photo' in self.fields):
            self.fields['photo'].widget.attrs['user'] = self.instance.user
        if ('diet' in self.fields):
            self.fields['diet'].widget.choices = self.instance.user.get_diet_choices()
            self.fields['diet'].initial = self.instance.user.diet
        if ('diet_match' in self.fields):
            # ~~~~ TODO: diet match choices gender is the desired match gender - either male, female or other. If more than one gender option is selected, then other. Same is for smoking status and marital status.
            self.fields['diet_match'].widget.choices = self.instance.user.get_diet_choices()
        for field_name, field in self.fields.items():
            if field_name in self._validators:
                field.validators = self._validators[field_name]

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
            if (self.instance.activation_step >= len(settings.SITE_PROFILE_FORM_FIELDS) - 1):
                self.instance.activation_step = len(settings.SITE_PROFILE_FORM_FIELDS)
            self.instance.save(update_fields={'activation_step'})
        return self.instance


class ProfileNotificationsForm(CoreProfileNotificationsForm):
    _profile_fields = ("notify_on_like", )


