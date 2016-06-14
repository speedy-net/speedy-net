from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, HTML, Row, Hidden
from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from speedy.core.forms import ModelFormWithDefaults
from speedy.core.mail import send_mail
from .models import User, UserEmailAddress, SiteProfile

DATE_FIELD_FORMATS = [
    '%Y-%m-%d',  # '2006-10-25'
    '%m/%d/%Y',  # '10/25/2006'
    '%m/%d/%y',  # '10/25/06'
    '%b %d %Y',  # 'Oct 25 2006'
    '%b %d, %Y',  # 'Oct 25, 2006'
    '%d %b %Y',  # '25 Oct 2006'
    '%d %b, %Y',  # '25 Oct, 2006'
    '%B %d %Y',  # 'October 25 2006'
    '%B %d, %Y',  # 'October 25, 2006'
    '%d %B %Y',  # '25 October 2006'
    '%d %B, %Y',  # '25 October, 2006'
]

DEFAULT_DATE_FIELD_FORMAT = '%B %d, %Y'


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
        self.fields['date_of_birth'].input_formats = DATE_FIELD_FORMATS
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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name_en', 'last_name_en', 'first_name_he', 'last_name_he', 'date_of_birth', 'profile_picture')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['date_of_birth'].input_formats = DATE_FIELD_FORMATS
        self.fields['date_of_birth'].widget.format = DEFAULT_DATE_FIELD_FORMAT
        self.helper = FormHelper()
        self.helper.add_input(Hidden('_form', 'account'))
        # split into two columns
        field_names = list(self.fields.keys())
        self.helper.add_layout(Div(*[
            Row(*[
                Div(field, css_class='col-md-6')
                for field in pair])
            for pair in zip(field_names[::2], field_names[1::2])
            ]))
        self.helper.add_input(Submit('submit', _('Save Changes')))


class ProfilePrivacyForm(forms.ModelForm):
    class Meta:
        model = SiteProfile
        fields = ('access_account', 'public_email')

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.add_input(Hidden('_form', 'privacy'))
        helper.add_input(Submit('submit', _('Save Changes')))
        return helper


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


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, **kwargs):
        user = kwargs.pop('user')
        super().__init__(user, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Hidden('_form', 'password'))
        self.helper.add_input(Submit('submit', _('Change')))


class UserEmailAddressForm(CleanEmailMixin, ModelFormWithDefaults):
    class Meta:
        model = UserEmailAddress
        fields = ('email',)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Add')))
        return helper
