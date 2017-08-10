import json

from django import forms
from django.conf import settings
from speedy.match.accounts import validators
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.sites.models import Site

from modeltranslation.forms import TranslationModelForm
from speedy.core.uploads.models import Image
from speedy.core.accounts.models import User
from speedy.core.accounts.forms import ProfileNotificationsForm as CoreProfileNotificationsForm

from .models import SiteProfile


class CustomPhotoWidget(forms.widgets.Widget):

    def render(self, name, value, attrs=None):
        language_code = get_language()
        SPEEDY_NET_SITE_ID = settings.SITE_PROFILES['net']['site_id']
        speedy_net_url = Site.objects.get(id=SPEEDY_NET_SITE_ID).domain
        return render_to_string('accounts/edit_profile/activation_form/photo_widget.html', {
            'name': name,
            'user_photo': self.attrs['user'].photo,
            'LANGUAGE_CODE': language_code,
            'speedy_net_url': speedy_net_url,
        })


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def value_from_datadict(self, data, files, name):
        return data.get(name)


class CustomJsonWidget(CustomCheckboxSelectMultiple):

    def render(self, name, value, attrs=None):
        return render_to_string('accounts/edit_profile/activation_form/json_widget.html', {'choices': self.choices, 'name': name,'value': json.loads(value)})


class SpeedyMatchProfileActivationForm(TranslationModelForm):
    # ~~~~ TODO: diet choices depend on the current user's gender. Also same for smoking and marital status.
    diet = forms.ChoiceField(choices=User.DIET_CHOICES[1:], widget=forms.RadioSelect(), label=_('My diet'), validators=[validators.validate_diet])
    photo = forms.ImageField(required=False, widget=CustomPhotoWidget, label=_('Add profile picture'))

    class Meta:
        model = SiteProfile
        fields = ('photo', 'profile_description', 'city', 'height', 'children', 'more_children', 'diet', 'smoking',
                  'marital_status', 'gender_to_match', 'match_description', 'min_age_match', 'max_age_match',
                  'diet_match', 'smoking_match', 'marital_status_match')
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
            'marital_status_match': CustomJsonWidget(choices=SiteProfile.MARITAL_STATUS_CHOICES)
        }

    def clean_photo(self):
        photo = self.files.get('photo')
        if not photo:
            photo = self.instance.user.photo
        validators.validate_photo(photo=photo)
        return self.cleaned_data

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
        if ('photo' in self.fields):
            self.fields['photo'].widget.attrs['user'] = self.instance.user
        if ('diet' in self.fields):
            self.fields['diet'].widget.choices = self.instance.user.get_diet_choices()
            self.fields['diet'].initial = self.instance.user.diet
        if ('diet_match' in self.fields):
            # ~~~~ TODO: diet match choices gender is the desired match gender - either male, female or other. If more than one gender option is selected, then other. Same is for smoking and marital status.
            self.fields['diet_match'].widget.choices = self.instance.user.get_diet_choices()

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
            if (self.instance.activation_step - 1 >= len(settings.SITE_PROFILE_FORM_FIELDS)):
                self.instance.activation_step = 2
            self.instance.save(update_fields={'activation_step'})
        return self.instance


class ProfileNotificationsForm(CoreProfileNotificationsForm):
    profile_fields = ("notify_on_like", )
