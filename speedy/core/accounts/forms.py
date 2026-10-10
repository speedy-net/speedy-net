import logging

from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Submit, Div, HTML, Row, Hidden, Layout

from django import forms
from django.conf import settings as django_settings
from django.contrib.auth import forms as django_auth_forms, password_validation
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _, pgettext_lazy
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
    """
    Mixin that normalizes and validates the uniqueness of a form's `email` field.
    """

    def clean_email(self):
        """
        Normalize the submitted email address and validate that it is not already in use.

        :return: The normalized email address.
        :rtype: str
        :raises django.core.exceptions.ValidationError: If the email address is already in use.
        """
        email = self.cleaned_data['email']
        email = normalize_email(email=email)
        speedy_core_accounts_validators.validate_email_unique(email=email)
        return email


class CleanNewPasswordMixin(object):
    """
    Mixin that validates a form's `new_password1` field using Django's password validators.
    """

    def clean_new_password1(self):
        """
        Validate the submitted new password against Django's configured password validators.

        :return: The new password.
        :rtype: str
        :raises django.core.exceptions.ValidationError: If the password fails validation.
        """
        new_password = self.cleaned_data['new_password1']
        password_validation.validate_password(password=new_password)
        return new_password


class CleanDateOfBirthMixin(object):
    """
    Mixin that validates a form's `date_of_birth` field.
    """

    def clean_date_of_birth(self):
        """
        Validate the submitted date of birth.

        :return: The date of birth.
        :rtype: datetime.date
        :raises django.core.exceptions.ValidationError: If the date of birth is invalid.
        """
        date_of_birth = self.cleaned_data['date_of_birth']
        speedy_core_accounts_validators.validate_date_of_birth_in_forms(date_of_birth=date_of_birth)
        return date_of_birth


class LocalizedFirstLastNameMixin(object):
    """
    Mixin that adds per-language first/last name fields to a form, and keeps them in sync with the form's `User` instance.

    Attributes:
        language_code (str): The language code used to determine which localized fields are required/labeled, taken from the `language_code` keyword argument.

    Methods:
        __init__(self, *args, **kwargs): Adds the localized name fields to the form, sets their initial values and ordering.
        save(self, commit=True): Saves the localized name field values onto the form's instance.
        get_localizable_fields(self): Returns the list of localizable field base names defined on the User model.
        get_required_localizable_fields(self): Returns the list of required localizable field base names defined on the User model.
        get_localized_field(self, base_field_name, language_code): Returns the attribute name of a localized field for a given base field name and language code.
        get_localized_fields(self, language=None): Returns the localized field attribute names for a given language (or the form's language).
        get_required_localized_fields(self, language=None): Returns the required localized field attribute names for a given language (or the form's language).
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, add the localized name fields, set their initial values and required status, and reorder the fields.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`. Must include `language_code`.
        """
        assert ('language_code' in kwargs)
        self.language_code = kwargs.pop('language_code', 'en')
        super().__init__(*args, **kwargs)
        localized_fields = self.get_localized_fields()
        required_localized_fields = self.get_required_localized_fields()
        for loc_field in localized_fields:
            self.fields[loc_field] = User._meta.get_field(loc_field).formfield()
            if (loc_field in required_localized_fields):
                self.fields[loc_field].required = True
            if (loc_field == self.get_localized_field(base_field_name="last_name", language_code=self.language_code)):
                self.fields[loc_field].label = _('Last name (optional)')
            self.initial[loc_field] = getattr(self.instance, loc_field, '')
        self.order_fields(field_order=localized_fields)

    def save(self, commit=True):
        """
        Save the localized name field values from cleaned data onto the form's instance.

        :param commit: Whether to save the instance to the database. Defaults to True.
        :type commit: bool
        :return: The updated instance.
        :rtype: speedy.core.accounts.models.User
        """
        instance = super().save(commit=False)
        for loc_field in self.get_localized_fields():
            setattr(instance, loc_field, self.cleaned_data[loc_field])
        if (commit):
            instance.save()
        return instance

    @staticmethod
    def get_localizable_fields():
        """
        Return the list of localizable field base names defined on the User model.

        :return: The localizable field base names.
        :rtype: tuple
        """
        return User.NAME_LOCALIZABLE_FIELDS

    @staticmethod
    def get_required_localizable_fields():
        """
        Return the list of required localizable field base names defined on the User model.

        :return: The required localizable field base names.
        :rtype: tuple
        """
        return User.NAME_REQUIRED_LOCALIZABLE_FIELDS

    def get_localized_field(self, base_field_name, language_code):
        """
        Return the attribute name of a localized field for a given base field name and language code.

        :param base_field_name: The base field name (e.g. "first_name").
        :type base_field_name: str
        :param language_code: The language code to localize for, or None to use the form's language code.
        :type language_code: str or None
        :return: The localized field's attribute name.
        :rtype: str
        """
        return to_attribute(name=base_field_name, language_code=language_code or self.language_code)

    def get_localized_fields(self, language=None):
        """
        Return the localized field attribute names for all localizable fields, for a given language.

        :param language: The language code to localize for, or None to use the form's language code.
        :type language: str or None
        :return: The localized field attribute names.
        :rtype: list
        """
        loc_fields = self.get_localizable_fields()
        return [self.get_localized_field(base_field_name=loc_field, language_code=language or self.language_code) for loc_field in loc_fields]

    def get_required_localized_fields(self, language=None):
        """
        Return the localized field attribute names for all required localizable fields, for a given language.

        :param language: The language code to localize for, or None to use the form's language code.
        :type language: str or None
        :return: The required localized field attribute names.
        :rtype: list
        """
        loc_fields = self.get_required_localizable_fields()
        return [self.get_localized_field(base_field_name=loc_field, language_code=language or self.language_code) for loc_field in loc_fields]


class AddAttributesToFieldsMixin(object):
    """
    Mixin that adds HTML widget attributes (such as disabling autocomplete/autocorrect) to a configured set of form fields, and forces left-to-right direction for some of them.

    Attributes:
        attribute_fields (list): Names of fields that should get the extra widget attributes.
        ltr_attribute_fields (list): Names of fields (a subset of `attribute_fields`) that should also be forced to left-to-right direction.
    """

    attribute_fields = ['slug', 'username', 'email', 'sender_email', 'new_password1', 'new_password2', 'old_password', 'password', 'date_of_birth']
    ltr_attribute_fields = ['slug', 'username', 'email', 'sender_email', 'new_password1', 'new_password2', 'old_password', 'password']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and add HTML widget attributes to the configured fields.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
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
    """
    Custom widget that renders a user's profile picture using a dedicated template, instead of a standard file input.

    Attributes:
        needs_multipart_form (bool): Indicates that the widget requires a multipart form.
    """

    needs_multipart_form = True

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the widget using the photo widget template, based on the user set in `self.attrs['user']`.

        :param name: The name of the form field.
        :type name: str
        :param value: The value of the form field.
        :param attrs: Optional additional widget attributes.
        :type attrs: dict or None
        :param renderer: Optional form renderer.
        :return: The rendered HTML for the widget.
        :rtype: str
        """
        return render_to_string(template_name='accounts/edit_profile/widgets/photo_widget.html', context={
            'name': name,
            'user_photo': self.attrs['user'].photo,
        })


class RegistrationForm(AddAttributesToFieldsMixin, CleanEmailMixin, CleanNewPasswordMixin, CleanDateOfBirthMixin, LocalizedFirstLastNameMixin, forms.ModelForm):
    """
    Form used to register a new user account, including email, username, password, gender, date of birth and localized name fields.

    Attributes:
        email (EmailField): The user's email address.
        new_password1 (CharField): The user's chosen password.

    Methods:
        __init__(self, *args, **kwargs): Sets labels, date input formats, and the crispy forms helper.
        save(self, commit=True): Creates the user, sets the password, saves localized names, and creates the primary email address.
    """

    email = forms.EmailField(label=_('Your email'), required=True)
    new_password1 = forms.CharField(label=_("New password"), strip=False, widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('email', 'slug', 'new_password1', 'gender', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, customize the username label, set the date of birth input formats, and configure the crispy forms helper.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
        super().__init__(*args, **kwargs)
        self.fields['slug'].label = _('New username')
        self.fields['date_of_birth'].input_formats = django_settings.DATE_FIELD_FORMATS
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', _('Create an account'), css_class='btn-lg btn-arrow-right'))

    def save(self, commit=True):
        """
        Create the new user, set their password, save their localized names, and (if committed) create their primary email address and log the registration.

        :param commit: Whether to save the user to the database. Defaults to True.
        :type commit: bool
        :return: The new user.
        :rtype: speedy.core.accounts.models.User
        """
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
            language_code = get_language()
            logger.info('New user on {site_name}, user={user}, email={email}, date of birth={date_of_birth}, language_code={language_code}.'.format(
                site_name=_(site.name),
                user=user,
                email=email,
                date_of_birth=user.date_of_birth,
                language_code=language_code,
            ))
        return user


class ProfileForm(AddAttributesToFieldsMixin, CleanDateOfBirthMixin, LocalizedFirstLastNameMixin, forms.ModelForm):
    """
    Form used by a user to edit their own profile, including username, gender, date of birth, profile picture and localized name fields.

    Attributes:
        profile_picture (ImageField): The user's uploaded profile picture.

    Methods:
        __init__(self, *args, **kwargs): Sets up labels, date input formats, and a two-column crispy forms layout.
        get_field_pairs(self): Returns the field names grouped as pairs for the two-column layout.
        clean_profile_picture(self): Validates and stages the uploaded profile picture.
        clean_slug(self): Validates that the username (slug) was not changed.
        save(self, commit=True): Saves the profile, applies the new profile picture, and logs date of birth/gender/username changes.
    """

    profile_picture = forms.ImageField(required=False, widget=CustomPhotoWidget, label=_('Update your profile picture'), error_messages={'required': _("A profile picture is required.")})

    class Meta:
        model = User
        fields = ('slug', 'gender', 'date_of_birth', 'profile_picture')

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, customize labels for the current gender, and configure the two-column crispy forms layout.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
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
        self.helper.layout.append(
            HTML('<button type="submit" title="{button_text}" class="btn btn-primary"><i class="fas fa-save"></i><span class="label ml-2">{button_text}</span></button>'.format(
                button_text=pgettext_lazy(context=self.instance.get_gender(), message='Save Changes'),
            )),
        )

    def get_field_pairs(self):
        """
        Return the form's field names grouped as pairs, used to render the fields in a two-column layout.

        :return: A tuple of field name tuples.
        :rtype: tuple
        """
        return ((to_attribute(name='first_name'), to_attribute(name='last_name')), ('slug',), ('gender', 'date_of_birth'), ('profile_picture',))

    def clean_profile_picture(self):
        """
        Validate the uploaded profile picture (if any), staging it as a new `Image` instance, or validate the existing photo if no new picture was uploaded.

        :return: The profile picture value.
        :raises django.core.exceptions.ValidationError: If the profile picture is invalid.
        """
        profile_picture = self.files.get('profile_picture')
        if (profile_picture):
            user_image = Image(owner=self.instance, file=profile_picture)
            user_image.save()
            self.instance._new_profile_picture = user_image
            try:
                speedy_core_accounts_validators.validate_image_file_extension(value=profile_picture)
                speedy_core_accounts_validators.validate_profile_picture_for_user(user=self.instance, profile_picture=profile_picture, test_new_profile_picture=True)
            except ValidationError:
                user_image.file.delete(save=False)
                user_image.delete()
                raise
        else:
            if (self.instance.photo):
                profile_picture = self.instance.photo
                speedy_core_accounts_validators.validate_profile_picture_for_user(user=self.instance, profile_picture=profile_picture, test_new_profile_picture=False)
        return self.cleaned_data.get('profile_picture')

    def clean_slug(self):
        """
        Validate that the submitted slug normalizes to the same username as the existing instance, since users can't change their username.

        :return: The slug.
        :rtype: str
        :raises django.core.exceptions.ValidationError: If the slug would change the username.
        """
        slug = self.cleaned_data.get('slug')
        username = self.instance.username
        if (not (normalize_username(username=slug) == username)):
            raise ValidationError(pgettext_lazy(context=self.instance.get_gender(), message="You can't change your username."))
        return slug

    def save(self, commit=True):
        """
        Save the profile, applying any new profile picture, and (if committed) logging changes to date of birth, gender and username.

        :param commit: Whether to save the instance to the database. Defaults to True.
        :type commit: bool
        :return: The saved user.
        :rtype: speedy.core.accounts.models.User
        """
        if (commit):
            if ('profile_picture' in self.fields):
                profile_picture = self.files.get('profile_picture')
                if (profile_picture):
                    self.instance.photo = self.instance._new_profile_picture
                    if (self.instance.speedy_match_profile):
                        self.instance.speedy_match_profile.profile_picture_months_offset = 5
                        self.instance.speedy_match_profile.save()
            user = User.objects.get(pk=self.instance.pk)
            if (not (self.instance.date_of_birth == user.date_of_birth)):
                self.instance.number_of_date_of_birth_changes += 1
                site = Site.objects.get_current()
                language_code = get_language()
                logger.warning('User changed date of birth on {site_name}, user={user}, new date of birth={new_date_of_birth}, old date of birth={old_date_of_birth} (registered {registered_days_ago} days ago), number_of_date_of_birth_changes={number_of_date_of_birth_changes}, language_code={language_code}.'.format(
                    site_name=_(site.name),
                    user=self.instance,
                    new_date_of_birth=self.instance.date_of_birth,
                    old_date_of_birth=user.date_of_birth,
                    registered_days_ago=(now() - self.instance.date_created).days,
                    number_of_date_of_birth_changes=self.instance.number_of_date_of_birth_changes,
                    language_code=language_code,
                ))
            if (not (self.instance.gender == user.gender)):
                site = Site.objects.get_current()
                language_code = get_language()
                logger.warning('User changed gender on {site_name}, user={user}, new gender={new_gender}, old gender={old_gender} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                    site_name=_(site.name),
                    user=self.instance,
                    new_gender=self.instance.gender,
                    old_gender=user.gender,
                    registered_days_ago=(now() - self.instance.date_created).days,
                    language_code=language_code,
                ))
            if (not (self.instance.username == user.username)):
                # Error - users can't change their username.
                site = Site.objects.get_current()
                language_code = get_language()
                logger.error('User changed username on {site_name}, user={user}, new username={new_username}, old username={old_username} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                    site_name=_(site.name),
                    user=self.instance,
                    new_username=self.instance.username,
                    old_username=user.username,
                    registered_days_ago=(now() - self.instance.date_created).days,
                    language_code=language_code,
                ))
        return super().save(commit=commit)


class ProfileNotificationsForm(forms.ModelForm):
    """
    Form used to edit a user's notification settings, including both User-level fields and site-specific profile fields.

    Attributes:
        _profile_model (type): The site profile model class used to look up additional profile fields.
        _profile_fields (tuple): Names of site profile fields to expose on the form (overridden by subclasses).

    Methods:
        __init__(self, *args, **kwargs): Adds the configured site profile fields to the form and sets up the crispy forms helper.
        save(self, commit=True): Saves the site profile fields onto the user's profile.
    """

    _profile_model = get_site_profile_model(profile_model=None)
    _profile_fields = ()

    class Meta:
        model = User
        fields = ('notify_on_message',)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, add the configured site profile fields with their current values, and configure the crispy forms helper.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
        super().__init__(*args, **kwargs)
        for field in self._profile_model._meta.fields:
            if (field.name in self._profile_fields):
                self.fields[field.name] = field.formfield()
                self.fields[field.name].initial = getattr(self.instance.profile, field.name)
        self.helper = FormHelperWithDefaults()
        self.helper.add_default_layout(form=self)
        self.helper.layout.append(
            HTML('<button type="submit" title="{button_text}" class="btn btn-primary"><i class="fas fa-save"></i><span class="label ml-2">{button_text}</span></button>'.format(
                button_text=pgettext_lazy(context=self.instance.get_gender(), message='Save Changes'),
            )),
        )

    def save(self, commit=True):
        """
        Save the User fields as usual, and additionally save the site profile fields onto the user's profile.

        :param commit: Whether to save the instance(s) to the database. Defaults to True.
        :type commit: bool
        :return: The saved user.
        :rtype: speedy.core.accounts.models.User
        """
        for field_name in self.fields.keys():
            if (field_name in self._profile_fields):
                setattr(self.instance.profile, field_name, self.cleaned_data[field_name])
        return_value = super().save(commit=commit)
        if (commit):
            self.instance.profile.save()
        return return_value


class LoginForm(AddAttributesToFieldsMixin, django_auth_forms.AuthenticationForm):
    """
    Login form that allows the user to log in with either their email address or username, and is not restricted to active users only.

    Methods:
        __init__(self, *args, **kwargs): Lowercases the submitted username, customizes labels, and sets up the crispy forms layout.
        confirm_login_allowed(self, user): Allows login regardless of the user's active status.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, lowercase the submitted username (which may be an email address), and configure the crispy forms layout.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
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
                    link=reverse(viewname='accounts:password_reset'),
                    text=_('Forgot your password?'),
                )),
            ),
        )

    def confirm_login_allowed(self, user):
        """
        Allow login regardless of whether the user is active, overriding the default Django behavior.

        :param user: The user attempting to log in.
        :type user: speedy.core.accounts.models.User
        :return: None, always allowing the login to proceed.
        :rtype: None
        """
        return None


class PasswordResetForm(django_auth_forms.PasswordResetForm):
    """
    Password reset form that looks up users by confirmed email address, logs reset requests, and sends the reset email using the project's own mail sending mechanism.

    Methods:
        helper(self): Returns the crispy forms helper used to render the submit button.
        get_users(self, email): Returns the users matching the given email address who should receive a reset.
        send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None): Sends the password reset email.
        save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt', email_template_name='registration/password_reset_email.html', use_https=False, token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None, extra_email_context=None): Generates a reset link for each matching user and sends it to them.
    """

    @property
    def helper(self):
        """
        Build the crispy forms helper used to render the submit button.

        :return: The form helper.
        :rtype: speedy.core.base.forms.FormHelperWithDefaults
        """
        helper = FormHelperWithDefaults()
        helper.add_input(Submit('submit', _('Submit')))
        return helper

    def get_users(self, email):
        """
        Given an email, return matching user(s) who should receive a reset.

        :param email: The email address to look up.
        :type email: str
        :return: The set of users with a confirmed email address matching `email` and a usable password.
        :rtype: set
        """
        email_addresses = UserEmailAddress.objects.prefetch_related('user').filter(email__iexact=email.lower())
        return {e.user for e in email_addresses if ((e.email == email.lower()) and (e.user.has_usable_password()))}

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.

        :param subject_template_name: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param email_template_name: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param context: The template context for the email.
        :type context: dict
        :param from_email: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param to_email: The recipient email address.
        :type to_email: str
        :param html_email_template_name: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :return: None
        """
        send_mail(to=[to_email], template_name_prefix='email/accounts/password_reset', context=context)

    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt', email_template_name='registration/password_reset_email.html', use_https=False, token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None, extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the user.

        :param domain_override: Optional domain to use instead of the current site's domain.
        :param subject_template_name: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param email_template_name: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param use_https: Whether to use https in the generated link. Defaults to False.
        :type use_https: bool
        :param token_generator: The token generator used to create the reset token. Defaults to `default_token_generator`.
        :param from_email: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param request: The current request, used to determine the current site when `domain_override` is not given.
        :param html_email_template_name: Unused. Kept for compatibility with Django's PasswordResetForm signature.
        :param extra_email_context: Optional extra context to merge into the email template context.
        :type extra_email_context: dict or None
        :return: None
        """
        email = self.cleaned_data["email"]
        site = Site.objects.get_current()
        users_list = self.get_users(email=email)
        language_code = get_language()
        logger.info("PasswordResetForm::User submitted form, site_name={site_name}, email={email}, matching_users={matching_users}, language_code={language_code}.".format(
            site_name=_(site.name),
            email=email,
            matching_users=len(users_list),
            language_code=language_code,
        ))
        for user in users_list:
            if (not (domain_override)):
                current_site = get_current_site(request=request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            user_email_list = [e.email for e in user.email_addresses.all() if (e.email == email.lower())]
            if (len(user_email_list) == 1):
                user_email = user_email_list[0]
                logger.info("PasswordResetForm::Sending reset link to the user, site_name={site_name}, user={user}, user_email={user_email} (registered {registered_days_ago} days ago), language_code={language_code}.".format(
                    site_name=_(site_name),
                    user=user,
                    user_email=user_email,
                    registered_days_ago=(now() - user.date_created).days,
                    language_code=language_code,
                ))
                context = {
                    'email': user_email,
                    'domain': domain,  # Taken from Django; not used.
                    'site_name': site_name,  # Taken from Django; not used.
                    'uid': urlsafe_base64_encode(s=force_bytes(s=user.pk)),
                    'user': user,
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',  # Taken from Django; not used.
                    **(extra_email_context or {}),
                }
                self.send_mail(subject_template_name=subject_template_name, email_template_name=email_template_name, context=context, from_email=from_email, to_email=user_email, html_email_template_name=html_email_template_name)
            else:
                logger.error("PasswordResetForm::User doesn't have a matching email address, site_name={site_name}, user={user}, email={email} (registered {registered_days_ago} days ago), language_code={language_code}.".format(
                    site_name=_(site_name),
                    user=user,
                    email=email,
                    registered_days_ago=(now() - user.date_created).days,
                    language_code=language_code,
                ))


class SetPasswordForm(AddAttributesToFieldsMixin, CleanNewPasswordMixin, django_auth_forms.SetPasswordForm):
    """
    Form used to set a new password for a user without requiring their old password (e.g. as part of the password reset flow).

    Methods:
        helper(self): Returns the crispy forms helper used to render the submit button.
    """

    @property
    def helper(self):
        """
        Build the crispy forms helper used to render the submit button.

        :return: The form helper.
        :rtype: speedy.core.base.forms.FormHelperWithDefaults
        """
        helper = FormHelperWithDefaults()
        helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Change Password')))
        return helper


class PasswordChangeForm(AddAttributesToFieldsMixin, CleanNewPasswordMixin, django_auth_forms.PasswordChangeForm):
    """
    Form used by a logged-in user to change their password, requiring their current password.

    Methods:
        __init__(self, *args, **kwargs): Configures the crispy forms helper, including a hidden field marking the form.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and configure the crispy forms helper.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Hidden('_form', 'password'))
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Change Password')))


class SiteProfileActivationForm(forms.ModelForm):
    """
    Form used to activate a user's site profile (e.g. Speedy Net or Speedy Match profile).

    Methods:
        __init__(self, *args, **kwargs): Configures the crispy forms helper with a submit button.
        save(self, commit=True): Activates the site profile and saves the form.
    """

    class Meta:
        model = get_site_profile_model(profile_model=None)
        fields = ()

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and configure the crispy forms helper with a submit button.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
        super().__init__(*args, **kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.instance.user.get_gender(), message='Activate your {site_name} account').format(site_name=_(site.name))))

    def save(self, commit=True):
        """
        Activate the site profile (if committed) and save the form.

        :param commit: Whether to save the instance to the database. Defaults to True.
        :type commit: bool
        :return: The saved site profile instance.
        """
        if (commit):
            self.instance.activate()
        return super().save(commit=commit)


class SiteProfileDeactivationForm(AddAttributesToFieldsMixin, forms.Form):
    """
    Form used to deactivate a user's site profile, requiring the user to confirm their password.

    Attributes:
        password (CharField): The user's current password, used to confirm the deactivation.

    Methods:
        __init__(self, *args, **kwargs): Stores the user and configures the crispy forms helper.
        clean_password(self): Validates that the submitted password matches the user's current password.
    """

    password = forms.CharField(label=_('Your password'), strip=False, widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        """
        Initialize the form, storing the user to deactivate and configuring the crispy forms helper.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`. Must include `user`.
        """
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Deactivate your {site_name} account').format(site_name=_(site.name)), css_class='btn-danger'))

    def clean_password(self):
        """
        Validate that the submitted password matches the user's current password.

        :return: The password.
        :rtype: str
        :raises django.core.exceptions.ValidationError: If the password does not match.
        """
        password = self.cleaned_data['password']
        if (not (self.user.check_password(raw_password=password))):
            raise ValidationError(_('Invalid password.'))
        return password


class UserEmailAddressForm(AddAttributesToFieldsMixin, CleanEmailMixin, ModelFormWithDefaults):
    """
    Form used to add a new email address to a user's account.

    Methods:
        helper(self): Returns the crispy forms helper used to render the submit button.
    """

    @property
    def helper(self):
        """
        Build the crispy forms helper used to render the submit button.

        :return: The form helper.
        :rtype: speedy.core.base.forms.FormHelperWithDefaults
        """
        helper = FormHelperWithDefaults()
        helper.add_input(Submit('submit', pgettext_lazy(context=self.defaults['user'].get_gender(), message='Add')))
        return helper

    class Meta:
        model = UserEmailAddress
        fields = ('email',)


class UserEmailAddressPrivacyForm(ModelFormWithDefaults):
    """
    Form used to change the access/privacy level of one of a user's email addresses.

    Methods:
        helper(self): Returns the crispy forms helper used to render the inline access field.
    """

    @property
    def helper(self):
        """
        Build the crispy forms helper used to render the inline access field, with a custom form action and template.

        :return: The form helper.
        :rtype: speedy.core.base.forms.FormHelperWithDefaults
        """
        helper = FormHelperWithDefaults()
        helper.form_class = 'form-inline'
        helper.form_action = reverse(viewname='accounts:change_email_privacy', kwargs={'pk': self.instance.id})
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            InlineField('access', css_class='input-sm'),
        )
        return helper

    class Meta:
        model = UserEmailAddress
        fields = ('access',)


class ProfilePrivacyForm(forms.ModelForm):
    """
    Form used to change the privacy/access level of a user's date of birth fields.

    Methods:
        __init__(self, *args, **kwargs): Configures the crispy forms helper and layout.
    """

    class Meta:
        fields = ('access_dob_day_month', 'access_dob_year')
        model = User

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and configure the crispy forms helper and layout.

        :param args: Positional arguments passed to the parent form's `__init__`.
        :param kwargs: Keyword arguments passed to the parent form's `__init__`.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelperWithDefaults()
        self.helper.add_default_layout(form=self)
        self.helper.layout.append(
            HTML('<button type="submit" title="{button_text}" class="btn btn-primary"><i class="fas fa-save"></i><span class="label ml-2">{button_text}</span></button>'.format(
                button_text=pgettext_lazy(context=self.instance.get_gender(), message='Save Changes'),
            )),
        )


