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
from speedy.core.accounts.forms import AddAttributesToFieldsMixin
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.base.mail import send_mail
from speedy.core.base.utils import normalize_username, to_attribute
from speedy.core.uploads.models import Image
from .models import User, UserEmailAddress
from .utils import normalize_email
from . import validators as speedy_core_accounts_validators

logger = logging.getLogger(__name__)


class DeleteAccountForm(AddAttributesToFieldsMixin, forms.Form):
    password = forms.CharField(label=_('Your password'), strip=False, widget=forms.PasswordInput, required=True)
    delete_my_account = forms.CharField(label=_('_______'), required=True)

    def __init__(self, *args, **kwargs):
        assert (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        site = Site.objects.get_current()
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='_____Permanently delete your {site_name} account').format(site_name=_(site.name)), css_class='btn-danger'))

    def clean_password(self):
        password = self.cleaned_data['password']
        if (not (self.user.check_password(raw_password=password))):
            raise ValidationError(_('Invalid password.'))
        return password

    def clean_delete_my_account(self):
        delete_my_account = self.cleaned_data['delete_my_account']
        if (not (delete_my_account == _("Yes. Delete my account."))):
            raise ValidationError(_('_______________'))
        return delete_my_account


