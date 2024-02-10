from django.conf import settings as django_settings

from rules import add_perm, is_authenticated

from speedy.core.accounts.base_rules import is_self, is_active
from speedy.core.accounts.rules import has_access_perm


if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
    add_perm('accounts.view_blocked_users_list', has_access_perm & is_self)
    add_perm('accounts.delete_account', is_authenticated & ~has_access_perm & ~is_active & is_self)


