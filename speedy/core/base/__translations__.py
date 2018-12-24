# This file is only for ./make_all_messages.sh, it is not used otherwise.

from django.utils.translation import gettext_lazy as _, ngettext_lazy


_('Enter a valid email address.')
_("Email address")
_("email address")
_("Email address:")
_("Email")
_("Value must be valid JSON.")


ngettext_lazy(
    singular='List contains %(show_value)d item, it should contain no more than %(limit_value)d.',
    plural='List contains %(show_value)d items, it should contain no more than %(limit_value)d.',
    number='limit_value'
)


