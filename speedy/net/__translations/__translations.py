# This file is only for ./make_all_messages.sh, it is not used otherwise.

from django.utils.translation import gettext_lazy as _, ngettext_lazy, pgettext_lazy


pgettext_lazy(context="female", message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.')
pgettext_lazy(context="male", message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.')
pgettext_lazy(context="other", message='Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.')

pgettext_lazy(context="female", message='Permanently delete your {site_name} account')
pgettext_lazy(context="male", message='Permanently delete your {site_name} account')
pgettext_lazy(context="other", message='Permanently delete your {site_name} account')

pgettext_lazy(context="female", message='Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using {site_name}.')
pgettext_lazy(context="male", message='Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using {site_name}.')
pgettext_lazy(context="other", message='Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using {site_name}.')

