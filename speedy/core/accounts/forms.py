import logging
from itertools import zip_longest

from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Submit, Div, HTML, Row, Hidden, Layout
from django import forms
from django.conf import settings as django_settings
from django.contrib.auth import forms as auth_forms, password_validation
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from speedy.core.base.forms import ModelFormWithDefaults, FormHelperWithDefaults
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.base.mail import send_mail
from speedy.core.base.utils import normalize_username, to_attribute
from speedy.core.uploads.models import Image
from .models import User, UserEmailAddress
from .utils import normalize_email
from . import validators as speedy_core_accounts_validators

logger = logging.getLogger(__name__)


class CleanEmailMixin(object):
    def clean_email(self):
        email = self.cleaned_data['email']
        email = normalize_email(email=email)
        speedy_core_accounts_validators.validate_email_unique(email=email)
        return email


class CleanNewPasswordMixin(object):
    def clean_new_password1(self):
        new_password = self.cleaned_data['new_password1']
        password_validation.validate_password(password=new_password)
        return new_password


class CleanDateOfBirthMixin(object):
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data['date_of_birth']
        speedy_core_accounts_validators.validate_date_of_birth_in_forms(date_of_birth=date_of_birth)
        return date_of_birth


class LocalizedFirstLastNameMixin(object):
    def __init__(self, *args, **kwargs):
        self.language_code = kwargs.pop('language_code', 'en')
        super().__init__(*args, **kwargs)
        localized_fields = self.get_localized_fields()
        for loc_field in localized_fields:
            self.fields[loc_field] = User._meta.get_field(loc_field).formfield()
            self.fields[loc_field].required = True
            self.initial[loc_field] = getattr(self.instance, loc_field, '')
        self.order_fields(field_order=localized_fields)

    def save(self, commit=True):
        instance = super().save(commit=False)
        for loc_field in self.get_localized_fields():
            setattr(instance, loc_field, self.cleaned_data[loc_field])
        if (commit):
            instance.save()
        return instance

    @staticmethod
    def get_localizable_fields():
        return User.NAME_LOCALIZABLE_FIELDS

    def get_localized_field(self, base_field_name, language_code):
        return to_attribute(name=base_field_name, language_code=language_code or self.language_code)

    def get_localized_fields(self, language=None):
        loc_fields = self.get_localizable_fields()
        return [self.get_localized_field(base_field_name=loc_field, language_code=language or self.language_code) for loc_field in loc_fields]


class AddAttributesToFieldsMixin(object):
    attribute_fields = ['slug', 'username', 'email', 'new_password1', 'new_password2', 'old_password', 'password', 'date_of_birth']
    ltr_attribute_fields = ['slug', 'username', 'email', 'new_password1', 'new_password2', 'old_password', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if (field_name in self.attribute_fields):
                field_widget_attrs_update_dict = {
                    'autocomplete': 'off',
                    'autocorrect': 'off',
                    'autocapitalize': 'off',
                    'spellcheck': 'false',
                }
                if (field_name in self.ltr_attribute_fields):
                    field_widget_classes = field.widget.attrs.get("class", "")
                    field_widget_classes = "{} direction-ltr".format(field_widget_classes).strip()
                    field_widget_attrs_update_dict['class'] = field_widget_classes
                field.widget.attrs.update(field_widget_attrs_update_dict)


class CustomPhotoWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return render_to_string(template_name='accounts/edit_profile/activation_form/photo_widget.html', context={
            'name': name,
            'user_photo': self.attrs['user'].photo,
        })


class RegistrationForm(AddAttributesToFieldsMixin, CleanEmailMixin, CleanNewPasswordMixin, CleanDateOfBirthMixin, LocalizedFirstLastNameMixin, forms.ModelForm):
    email = forms.EmailField(label=_('Your email'))
    new_password1 = forms.CharField(label=_("New password"), strip=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'slug', 'new_password1', 'gender', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].label = _('New username')
        self.fields['date_of_birth'].input_formats = django_settings.DATE_FIELD_FORMATS
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', _('Create an account'), css_class='btn-lg btn-arrow-right'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(raw_password=self.cleaned_data["new_password1"])
        for language_code, language_name in django_settings.LANGUAGES:
            for loc_field in self.get_localizable_fields():
                setattr(user, self.get_localized_field(base_field_name=loc_field, language_code=language_code), self.cleaned_data[self.get_localized_field(base_field_name=loc_field, language_code=self.language_code)])
        if (commit):
            user.save()
            email = self.cleaned_data['email']
            user.email_addresses.create(email=email, is_confirmed=False, is_primary=True)
            site = Site.objects.get_current()
            logger.info('New user on {site_name}, user={user}, email={email}'.format(site_name=_(site.name), user=user, email=email))
        return user


class ProfileForm(AddAttributesToFieldsMixin, CleanDateOfBirthMixin, LocalizedFirstLastNameMixin, forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=CustomPhotoWidget, label=_('Update your profile picture'), error_messages={'required': _("A profile picture is required.")})

    class Meta:
        model = User
        fields = ('slug', 'gender', 'date_of_birth', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].label = pgettext_lazy(context=self.instance.get_gender(), message='username (slug)')
        self.fields['date_of_birth'].input_formats = django_settings.DATE_FIELD_FORMATS
        self.fields['date_of_birth'].widget.format = django_settings.DEFAULT_DATE_FIELD_FORMAT
        self.fields['profile_picture'].widget.attrs['user'] = self.instance
        self.fields['profile_picture'].label = pgettext_lazy(context=self.instance.get_gender(), message='Update your profile picture')
        self.helper = FormHelperWithDefaults()
        # split into two columns
        field_names = list(self.fields.keys())
        self.helper.add_layout(
            Div(*[
                Row(*[
                    Div(field, css_class='col-md-6')
                    for field in pair])
                for pair in self.get_field_pairs()
            ]),
        )
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.get_gender(), message='Save Changes')))

    def get_field_pairs(self):
        return ((to_attribute(name='first_name'), to_attribute(name='last_name')), ('slug', ), ('gender', 'date_of_birth'), ('photo', ))

    def clean_profile_picture(self):
        profile_picture = self.files.get('profile_picture')
        if (profile_picture):
            user_image = Image(owner=self.instance, file=profile_picture)
            user_image.save()
            self.instance._new_photo = user_image
            speedy_core_accounts_validators.validate_photo_for_user(user=self.instance, photo=profile_picture, test_new_photo=True)
        else:
            if (self.instance.photo):
                profile_picture = self.instance.photo
                speedy_core_accounts_validators.validate_photo_for_user(user=self.instance, photo=profile_picture, test_new_photo=False)
        return self.cleaned_data.get('profile_picture')

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        username = self.instance.username
        if (not (normalize_username(username=slug) == username)):
            raise ValidationError(pgettext_lazy(context=self.instance.get_gender(), message="You can't change your username."))
        return slug

    def save(self, commit=True):
        if (commit):
            if ('profile_picture' in self.fields):
                profile_picture = self.files.get('profile_picture')
                if (profile_picture):
                    self.instance.photo = self.instance._new_photo
            user = User.objects.get(pk=self.instance.pk)
            if (not (self.instance.date_of_birth == user.date_of_birth)):
                site = Site.objects.get_current()
                logger.warning('User changed date of birth on {site_name}, user={user}, new date of birth={new_date_of_birth}, old date of birth={old_date_of_birth}'.format(site_name=_(site.name), user=self.instance, new_date_of_birth=self.instance.date_of_birth, old_date_of_birth=user.date_of_birth))
            if (not (self.instance.gender == user.gender)):
                site = Site.objects.get_current()
                logger.warning('User changed gender on {site_name}, user={user}, new gender={new_gender}, old gender={old_gender}'.format(site_name=_(site.name), user=self.instance, new_gender=self.instance.gender, old_gender=user.gender))
            if (not (self.instance.username == user.username)):
                # Error - users can't change their username.
                site = Site.objects.get_current()
                logger.error('User changed username on {site_name}, user={user}, new username={new_username}, old username={old_username}'.format(site_name=_(site.name), user=self.instance, new_username=self.instance.username, old_username=user.username))
        return super().save(commit=commit)


class ProfileNotificationsForm(forms.ModelForm):
    _profile_model = get_site_profile_model(profile_model=None)
    _profile_fields = ()

    class Meta:
        model = User
        fields = ('notify_on_message',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self._profile_model._meta.fields:
            if (field.name in self._profile_fields):
                self.fields[field.name] = field.formfield()
                self.fields[field.name].initial = getattr(self.instance.profile, field.name)
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.get_gender(), message='Save Changes')))

    def save(self, commit=True):
        for field_name in self.fields.keys():
            if (field_name in self._profile_fields):
                setattr(self.instance.profile, field_name, self.cleaned_data[field_name])
        r = super().save(commit=commit)
        if (commit):
            self.instance.profile.save()
        return r


class LoginForm(AddAttributesToFieldsMixin, auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
        if ('username' in self.data):
            self.data['username'] = self.data['username'].lower()
        self.fields['username'].label = _('Email or Username')
        self.helper = FormHelperWithDefaults()
        self.helper.add_layout(
            Div(
                'username',
                'password',
                Submit('submit', _('Login')),
                HTML('<a class="btn btn-link" href="{link}">{text}</a>'.format(
                    link=reverse('accounts:password_reset'),
                    text=_('Forgot your password?'),
                )),
            ),
        )

    def confirm_login_allowed(self, user):
        return None


class PasswordResetForm(auth_forms.PasswordResetForm):
    @property
    def helper(self):
        helper = FormHelperWithDefaults()
        helper.add_input(Submit('submit', _('Submit')))
        return helper

    def get_users(self, email):
        """
        Given an email, return matching user(s) who should receive a reset.
        """
        email_addresses = UserEmailAddress.objects.prefetch_related('user').filter(email__iexact=email.lower())
        return {e.user for e in email_addresses if ((e.email == email.lower()) and (e.user.has_usable_password()))}

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        send_mail(to=[to_email], template_name_prefix='email/accounts/password_reset', context=context)

    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt', email_template_name='registration/password_reset_email.html', use_https=False, token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None, extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the user.
        """
        email = self.cleaned_data["email"]
        site = Site.objects.get_current()
        users_list = self.get_users(email)
        logger.info("PasswordResetForm::User submitted form, site_name={site_name}, email={email}, matching_users={matching_users}".format(site_name=_(site.name), email=email, matching_users=len(users_list)))
        for user in users_list:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            user_email_list = [e.email for e in user.email_addresses.all() if (e.email == email.lower())]
            if (len(user_email_list) == 1):
                user_email = user_email_list[0]
                logger.info("PasswordResetForm::Sending reset link to the user, site_name={site_name}, user={user}, user_email={user_email}".format(site_name=_(site_name), user=user, user_email=user_email))
                context = {
                    'email': user_email,
                    'domain': domain,  # Taken from Django; not used.
                    'site_name': site_name,  # Taken from Django; not used.
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',  # Taken from Django; not used.
                    **(extra_email_context or {}),
                }
                self.send_mail(subject_template_name, email_template_name, context, from_email, user_email, html_email_template_name=html_email_template_name)
            else:
                logger.error("PasswordResetForm::User doesn't have a matching email address, site_name={site_name}, user={user}, email={email}".format(site_name=_(site_name), user=user, email=email))


class SetPasswordForm(AddAttributesToFieldsMixin, CleanNewPasswordMixin, auth_forms.SetPasswordForm):
    @property
    def helper(self):
        helper = FormHelperWithDefaults()
        helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Change Password')))
        return helper


class PasswordChangeForm(AddAttributesToFieldsMixin, CleanNewPasswordMixin, auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Hidden('_form', 'password'))
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Change Password')))


class SiteProfileActivationForm(forms.ModelForm):
    class Meta:
        model = get_site_profile_model(profile_model=None)
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.user.get_gender(), message='Activate your {site_name} account').format(site_name=_(site.name))))

    def save(self, commit=True):
        if (commit):
            self.instance.activate()
        return super().save(commit=commit)


class SiteProfileDeactivationForm(AddAttributesToFieldsMixin, forms.Form):
    password = forms.CharField(label=_('Your password'), strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Deactivate your {site_name} account').format(site_name=_(site.name)), css_class='btn-danger'))

    def clean_password(self):
        password = self.cleaned_data['password']
        if (not (self.user.check_password(raw_password=password))):
            raise ValidationError(_('Invalid password.'))
        return password


class UserEmailAddressForm(AddAttributesToFieldsMixin, CleanEmailMixin, ModelFormWithDefaults):
    @property
    def helper(self):
        helper = FormHelperWithDefaults()
        helper.add_input(Submit('submit', pgettext_lazy(context=self.defaults['user'].get_gender(), message='Add')))
        return helper

    class Meta:
        model = UserEmailAddress
        fields = ('email',)


class UserEmailAddressPrivacyForm(ModelFormWithDefaults):
    @property
    def helper(self):
        helper = FormHelperWithDefaults()
        helper.form_class = 'form-inline'
        helper.form_action = reverse('accounts:change_email_privacy', kwargs={'pk': self.instance.id})
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            InlineField('access', css_class='input-sm'),
        )
        return helper

    class Meta:
        model = UserEmailAddress
        fields = ('access',)


class ProfilePrivacyForm(forms.ModelForm):
    class Meta:
        fields = ('access_dob_day_month', 'access_dob_year')
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.get_gender(), message='Save Changes')))


