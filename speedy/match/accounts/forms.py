import json

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from modeltranslation.forms import TranslationModelForm
from speedy.core.uploads.models import Image
# from django.db.models
from speedy.core.accounts.models import User
from speedy.net.accounts.forms import ProfilePrivacyForm as NetAccountPrivacyForm

from .models import SiteProfile


class AccountPrivacyForm(NetAccountPrivacyForm):
    class Meta(NetAccountPrivacyForm.Meta):
        model = SiteProfile
        fields = ()


class CustomPhotoWidget(forms.widgets.Widget):

    def render(self, name, value, attrs=None):
        return render_to_string('accounts/edit_profile/activation_form/photo_widget.html', {'name': name, 'user_photo': self.attrs['user'].photo})


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def value_from_datadict(self, data, files, name):
        return data.get(name)


class CustomJsonWidget(CustomCheckboxSelectMultiple):

    def render(self, name, value, attrs=None):
        return render_to_string('accounts/edit_profile/activation_form/json_widget.html', {'choices': self.choices, 'name': name,'value': json.loads(value)})


class SpeedyMatchProfileActivationForm(TranslationModelForm):

    diet = forms.ChoiceField(choices=User.DIET_CHOICES[1:], widget=forms.RadioSelect(), label=_('My diet'))
    photo = forms.ImageField(required=False, widget=CustomPhotoWidget, label=_('Add profile picture'))

    class Meta:
        model = SiteProfile
        fields = ('photo', 'profile_description', 'city', 'height', 'children', 'more_children', 'diet', 'smoking',
                  'marital_status', 'gender_to_match', 'match_description', 'min_age_match', 'max_age_match',
                  'diet_match', 'smoking_match', 'marital_match')
        widgets = {
            'profile_description': forms.Textarea(attrs={'rows': 3, 'cols': 25}),
            'children': forms.TextInput(),
            'more_children': forms.TextInput(),
            'smoking': forms.RadioSelect(),
            'marital_status': forms.RadioSelect(),
            'match_description': forms.Textarea(attrs={'rows': 3, 'cols': 25}),
            'gender_to_match': CustomCheckboxSelectMultiple(choices=User.GENDER_CHOICES),
            'diet_match': CustomJsonWidget(choices=User.DIET_CHOICES[1:]),
            'smoking_match': CustomJsonWidget(choices=SiteProfile.SMOKING_CHOICES),
            'marital_match': CustomJsonWidget(choices=SiteProfile.MARITAL_STATUS_CHOICES)
        }

    def get_fields(self):
        return settings.SITE_PROFILE_FORM_FIELDS[self.instance.activation_step]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.get_fields()
        fields_for_deletion = set(self.fields.keys()) - set(fields)
        for field_for_deletion in fields_for_deletion:
            del self.fields[field_for_deletion]
        if 'photo' in self.fields:
            self.fields['photo'].widget.attrs['user'] = self.instance.user

        if 'diet' in self.fields:
            self.fields['diet'].widget.choices = self.instance.user.get_diet_choices()
            if self.instance.user.diet != User.DIET_UNKNOWN:
                self.fields['diet'].initial = self.instance.user.diet
            else:
                self.fields['diet'].initial = User.DIET_VEGAN
        if 'diet_match' in self.fields:
            self.fields['diet_match'].widget.choices = self.instance.user.get_diet_choices()

    def save(self, commit=True):
        if commit and 'photo' in self.fields:
            if self.files:
                user_image = Image(owner=self.instance.user, file=self.files['photo'])
                user_image.save()
                self.instance.user.photo = user_image
            else:
                self.instance.user.photo = None
            self.instance.user.save()
        if commit and 'diet' in self.fields:
            self.instance.user.diet = self.cleaned_data['diet']
            self.instance.user.save()
        if commit:
            if self.instance.activation_step + 1 == len(settings.SITE_PROFILE_FORM_FIELDS):
                self.instance.activation_step = 0
                self.instance.activate()
            else:
                self.instance.activation_step += 1
        super().save(commit=commit)
        return self.instance
