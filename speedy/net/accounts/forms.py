from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, HTML
from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from speedy.core.forms import ModelFormWithDefaults
from speedy.core.mail import send_mail
from .models import User, UserEmailAddress


class CleanEmailMixin(object):
    def clean_email(self):
        email = self.cleaned_data['email']
        email = User.objects.normalize_email(email)
        if UserEmailAddress.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class RegistrationForm(CleanEmailMixin, auth_forms.UserCreationForm):
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
            email_address = user.email_addresses.create(
                email=self.cleaned_data['email'],
                is_confirmed=False,
                is_primary=True,
            )
        return user

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if slug in settings.UNAVAILABLE_USERNAMES:
            raise forms.ValidationError(_('This username is unavailable.'))
        return slug


class LoginForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Username or email')
        self.helper = FormHelper()
        self.helper.add_layout(Div(
            'username',
            'password',
            Submit('submit', _('Login')),
            HTML('<a class="btn btn-link" href="{link}">{text}</a>'.format(
                link=reverse('accounts:password_reset'),
                text=_('Forgot password?'),
            )),
        ))


class PasswordResetForm(auth_forms.PasswordResetForm):
    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Submit')))
        return helper

    def get_users(self, email):
        email_addresses = UserEmailAddress.objects.select_related('user') \
            .filter(email__iexact=email, is_confirmed=True)
        return {e.user for e in email_addresses if e.user.has_usable_password()}

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email,
                  html_email_template_name=None):
        send_mail([to_email], 'accounts/email/password_reset', context)


class SetPasswordForm(auth_forms.SetPasswordForm):
    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Submit')))
        return helper


class UserEmailAddressForm(CleanEmailMixin, ModelFormWithDefaults):
    class Meta:
        model = UserEmailAddress
        fields = ('email',)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Add')))
        return helper
