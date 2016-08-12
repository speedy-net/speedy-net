import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, HTML, Row, Hidden
from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from speedy.core.forms import ModelFormWithDefaults
from speedy.core.mail import send_mail
from .models import Entity, User, UserEmailAddress, SiteProfile
from .utils import get_site_profile_model

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
        email = email.lower()
        if UserEmailAddress.objects.filter(email=email).exists():
            # If this email address is not confirmed, delete it. Maybe another user added it but it belongs to the current user.
            UserEmailAddress.objects.filter(email=email, is_confirmed=False).delete()
            # If this email address is confirmed, raise an exception.
            if UserEmailAddress.objects.filter(email=email).exists():
                raise forms.ValidationError(_('This email is already in use.'))
        return email


class CleanNewPasswordMixin(object):
    def clean_new_password1(self):
        password = self.cleaned_data['new_password1']
        if len(password) < Entity.MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_('Password too short.'))
        if len(password) > Entity.MAX_PASSWORD_LENGTH:
            raise forms.ValidationError(_('Password too long.'))
        return password


class GetSlugAndUsernameMixin(object):
    def get_slug_and_username(self):
        # ~~~~ TODO: Same code here and in the model, combine to one code!
        slug = self.cleaned_data['slug']
        slug = slug.lower()
        slug = re.sub('[-\._]{1,}', '-', slug)
        slug = re.sub('^-', '', slug)
        slug = re.sub('-$', '', slug)
        username = re.sub('[-]', '', slug)
        return (slug, username)


class RegistrationForm(CleanEmailMixin, CleanNewPasswordMixin, GetSlugAndUsernameMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth')

    email = forms.EmailField(label=_('Your email'))
    new_password1 = forms.CharField(label=_("New password"), strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].label = _('New username')
        self.fields['date_of_birth'].input_formats = DATE_FIELD_FORMATS
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Create an account')))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
            email_address = user.email_addresses.create(
                email=self.cleaned_data['email'],
                is_confirmed=False,
                is_primary=True,
            )
        return user

    def clean_slug(self):
        slug, username = self.get_slug_and_username()
        # ~~~~ TODO: Same code here and in the model, combine to one code!
        if (len(username) < User.MIN_USERNAME_LENGTH):
            raise forms.ValidationError('Username is too short.')
        if (len(username) > User.MAX_USERNAME_LENGTH):
            raise forms.ValidationError('Username is too long.')
        pattern = re.compile("^([a-z]{4,}[0-9]{0,})$")
        if (not(pattern.match(username))):
            raise forms.ValidationError('Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.')
        if ((Entity.objects.filter(username=username).exists()) or (username in settings.UNAVAILABLE_USERNAMES)):
            raise forms.ValidationError(_('This username is already taken.'))
        return slug


class ProfileForm(GetSlugAndUsernameMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name_en', 'last_name_en', 'date_of_birth', 'photo', 'slug')

    def get_localized_fields(self):
        loc_fields = ('first_name', 'last_name')
        if self.language == 'en':
            return []
        return ['{}_{}'.format(loc_field, self.language) for loc_field in loc_fields]

    def __init__(self, **kwargs):
        self.language = kwargs.pop('language', 'en')
        super().__init__(**kwargs)
        for loc_field in reversed(self.get_localized_fields()):
            self.fields[loc_field] = User._meta.get_field(loc_field).formfield()
            self.fields.move_to_end(loc_field, last=False)
        self.fields['date_of_birth'].input_formats = DATE_FIELD_FORMATS
        self.fields['date_of_birth'].widget.format = DEFAULT_DATE_FIELD_FORMAT
        self.fields['slug'].label = _('Username (slug)')
        self.helper = FormHelper()
        # split into two columns
        field_names = list(self.fields.keys())
        self.helper.add_layout(Div(*[
            Row(*[
                Div(field, css_class='col-md-6')
                for field in pair])
            for pair in zip(field_names[::2], field_names[1::2])
            ]))
        self.helper.add_input(Submit('submit', _('Save Changes')))

    def clean_slug(self):
        slug, username = self.get_slug_and_username()
        if (not(username == self.instance.username)):
            raise forms.ValidationError(_("You can't change your username."))
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        for loc_field in self.get_localized_fields():
            setattr(instance, loc_field, self.cleaned_data[loc_field])
        if commit:
            instance.save()
        return instance


class ProfilePrivacyForm(forms.ModelForm):
    class Meta:
        model = SiteProfile
        fields = ('access_account', 'public_email')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['public_email'].queryset = UserEmailAddress.objects.filter(is_confirmed=True, user=self.instance.user)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Save Changes')))


class ProfileNotificationsForm(forms.ModelForm):
    class Meta:
        model = get_site_profile_model()
        fields = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self._meta.model._meta.fields:
            if field.name.startswith('notify_'):
                self.fields[field.name] = field.formfield()
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Save Changes')))

    def save(self, commit=True):
        for field_name in self.fields.keys():
            setattr(self.instance, field_name, self.cleaned_data[field_name])
        return super().save(commit=commit)


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

    def confirm_login_allowed(self, user):
        return None


class PasswordResetForm(auth_forms.PasswordResetForm):
    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Submit')))
        return helper

    def get_users(self, email):
        email_addresses = UserEmailAddress.objects.select_related('user').filter(email__iexact=email, user__is_active=True)
        return {e.user for e in email_addresses if e.user.has_usable_password()}

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        send_mail([to_email], 'accounts/email/password_reset', context)


class SetPasswordForm(CleanNewPasswordMixin, auth_forms.SetPasswordForm):
    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Submit')))
        return helper


class PasswordChangeForm(CleanNewPasswordMixin, auth_forms.PasswordChangeForm):
    def __init__(self, **kwargs):
        user = kwargs.pop('user')
        super().__init__(user, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Hidden('_form', 'password'))
        self.helper.add_input(Submit('submit', _('Change')))


class DeactivationForm(forms.Form):
    password = forms.CharField(label=_('Your password'), strip=False, widget=forms.PasswordInput)

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(**kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Deactivate your account'), css_class='btn-danger'))

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_('Invalid password'))
        return password


class ActivationForm(auth_forms.PasswordResetForm):
    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Send Activation Email')))
        return helper

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        del self.fields['email']

    def get_users(self, email):
        if self.user.is_active:
            return set()
        return {self.user}

    def _post_clean(self):
        self.cleaned_data['email'] = ''

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        send_mail([to_email], 'accounts/email/activate', context)


class UserEmailAddressForm(CleanEmailMixin, ModelFormWithDefaults):
    class Meta:
        model = UserEmailAddress
        fields = ('email',)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Add')))
        return helper
