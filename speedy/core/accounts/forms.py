from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, HTML, Row, Hidden, Layout, ButtonHolder
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.base.mail import send_mail
from speedy.core.base.utils import normalize_username
from .models import User, UserEmailAddress, SiteProfileBase


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


class ModelFormWithDefaults(forms.ModelForm):
    def __init__(self, **kwargs):
        self.defaults = kwargs.pop('defaults', {})
        super().__init__(**kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field, value in self.defaults.items():
            setattr(instance, field, value)
        if commit:
            instance.save()
        return instance


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
        if len(password) < User.MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_('Password too short.'))
        if len(password) > User.MAX_PASSWORD_LENGTH:
            raise forms.ValidationError(_('Password too long.'))
        return password


class LocalizedFirstLastNameMixin(object):
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language', 'en')
        super().__init__(*args, **kwargs)
        for loc_field in reversed(self.get_localized_fields()):
            self.fields[loc_field] = User._meta.get_field(loc_field).formfield()
            self.fields[loc_field].required = True
            self.fields.move_to_end(loc_field, last=False)
            self.initial[loc_field] = getattr(self.instance, loc_field, '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        for loc_field in self.get_localized_fields():
            setattr(instance, loc_field, self.cleaned_data[loc_field])
        if commit:
            instance.save()
        return instance

    def get_localized_fields(self):
        loc_fields = ('first_name', 'last_name')
        return ['{}_{}'.format(loc_field, self.language) for loc_field in loc_fields]


class AddAttributesToFieldsMixin(object):

    attribute_fields = ['slug', 'username', 'email', 'new_password1', 'new_password2', 'old_password', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.attribute_fields:
                field.widget.attrs.update({'autocomplete': 'off', 'autocorrect': 'off', 'autocapitalize' : 'off', 'spellcheck': 'false'})


class RegistrationForm(AddAttributesToFieldsMixin, CleanEmailMixin, CleanNewPasswordMixin, LocalizedFirstLastNameMixin, forms.ModelForm):
    email = forms.EmailField(label=_('Your email'))
    new_password1 = forms.CharField(label=_("New password"), strip=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'slug', 'new_password1', 'gender', 'date_of_birth')

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


class ProfileForm(AddAttributesToFieldsMixin, LocalizedFirstLastNameMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('date_of_birth', 'photo', 'slug', 'gender')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['date_of_birth'].input_formats = DATE_FIELD_FORMATS
        self.fields['date_of_birth'].widget.format = DEFAULT_DATE_FIELD_FORMAT
        self.fields['slug'].label = pgettext_lazy(context=self.instance.get_gender(), message='username (slug)')
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
        slug = self.cleaned_data.get('slug')
        username = self.instance.username
        if normalize_username(slug=slug) != username:
            raise forms.ValidationError(pgettext_lazy(context=self.instance.get_gender(), message='You can\'t change your username.'))
        return slug


class ProfileNotificationsForm(forms.ModelForm):
    class Meta:
        model = get_site_profile_model(profile_model=None)
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


class LoginForm(AddAttributesToFieldsMixin, auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
        if 'username' in self.data:
            self.data['username'] = self.data['username'].lower()
        self.fields['username'].label = _('Email or Username')
        self.helper = FormHelper()
        self.helper.add_layout(Div(
            'username',
            'password',
            Submit('submit', _('Login')),
            HTML('<a class="btn btn-link" href="{link}">{text}</a>'.format(
                link=reverse('accounts:password_reset'),
                text=_('Forgot your password?'),
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
        email_addresses = UserEmailAddress.objects.select_related('user').filter(email__iexact=email,
                                                                                 user__is_active=True)
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


class SetPasswordForm(AddAttributesToFieldsMixin, CleanNewPasswordMixin, auth_forms.SetPasswordForm):
    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Submit')))
        return helper


class PasswordChangeForm(AddAttributesToFieldsMixin, CleanNewPasswordMixin, auth_forms.PasswordChangeForm):
    def __init__(self, **kwargs):
        user = kwargs.pop('user')
        super().__init__(user, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Hidden('_form', 'password'))
        self.helper.add_input(Submit('submit', _('Change')))


class SiteProfileActivationForm(forms.ModelForm):
    class Meta:
        model = get_site_profile_model(profile_model=None)
        fields = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.user.get_gender(), message='Activate your {} account').format(_(site.name))))

    def save(self, commit=True):
        if commit:
            self.instance.activate()
        return super().save(commit=commit)


class SiteProfileDeactivationForm(AddAttributesToFieldsMixin, forms.Form):
    password = forms.CharField(label=_('Your password'), strip=False, widget=forms.PasswordInput)

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(**kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Deactivate your {} account').format(_(site.name)), css_class='btn-danger'))

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_('Invalid password.'))
        return password


class UserEmailAddressForm(AddAttributesToFieldsMixin, CleanEmailMixin, ModelFormWithDefaults):
    class Meta:
        model = UserEmailAddress
        fields = ('email',)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', _('Add')))
        return helper


class UserEmailAddressPrivacyForm(ModelFormWithDefaults):
    class Meta:
        model = UserEmailAddress
        fields = ('access',)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-inline'
        helper.form_action = reverse('accounts:change_email_privacy', kwargs={'pk': self.instance.id})
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            InlineField('access', css_class='input-sm'),
        )
        return helper


class ProfilePrivacyForm(forms.ModelForm):
    class Meta:
        fields = ()
        model = SiteProfileBase

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Save Changes')))
