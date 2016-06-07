from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from .models import User, UserEmailAddress


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'slug', 'password1', 'password2', 'gender', 'date_of_birth')

    email = forms.EmailField(label=_('Email'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].label = _('Username')
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Create an account')))

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.email_addresses.create(
                email=self.cleaned_data['email'],
            )
        return user

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if slug in settings.UNAVAILABLE_USERNAMES:
            raise forms.ValidationError('This username is unavailable.')
        return slug

    def clean_email(self):
        email = self.cleaned_data['email']
        email = User.objects.normalize_email(email)
        if UserEmailAddress.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Username or email')
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Login')))
