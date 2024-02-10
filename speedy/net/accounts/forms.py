import logging

from crispy_forms.layout import Submit

from django import forms
from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError

from speedy.core.base.forms import FormHelperWithDefaults
from speedy.core.accounts.forms import AddAttributesToFieldsMixin

logger = logging.getLogger(__name__)


class DeleteAccountForm(AddAttributesToFieldsMixin, forms.Form):
    password = forms.CharField(label=_('Your password'), strip=False, widget=forms.PasswordInput, required=True)
    delete_my_account_text = forms.CharField(label=_('Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.'), required=True)

    def __init__(self, *args, **kwargs):
        assert (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        site = Site.objects.get_current()
        self.fields['delete_my_account_text'].label = pgettext_lazy(context=self.user.get_gender(), message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.')
        self.helper = FormHelperWithDefaults()
        self.helper.add_input(Submit('submit', pgettext_lazy(context=self.user.get_gender(), message='Permanently delete your {site_name} account').format(site_name=_(site.name)), css_class='btn-danger'))

    def clean_password(self):
        password = self.cleaned_data['password']
        if (not (self.user.check_password(raw_password=password))):
            raise ValidationError(_('Invalid password.'))
        return password

    def clean_delete_my_account_text(self):
        delete_my_account_text = self.cleaned_data['delete_my_account_text']
        if (not (delete_my_account_text == _("Yes. Delete my account."))):
            raise ValidationError(pgettext_lazy(context=self.user.get_gender(), message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.'))
        return delete_my_account_text


