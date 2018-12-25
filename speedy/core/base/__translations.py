# This file is only for ./make_all_messages.sh, it is not used otherwise.

from django.utils.translation import gettext_lazy as _, ngettext_lazy, pgettext_lazy


_('Enter a valid email address.')
_("Email address")
_("email address")
_("Email address:")
_("Email")
_("Value must be valid JSON.")
_("Please enter a correct %(username)s and password. Note that both fields may be case-sensitive.")


ngettext_lazy(
    singular='List contains %(show_value)d item, it should contain no more than %(limit_value)d.',
    plural='List contains %(show_value)d items, it should contain no more than %(limit_value)d.',
    number='limit_value'
)


pgettext_lazy(context="female", message='Your new password has been saved.')
pgettext_lazy(context="male", message='Your new password has been saved.')
pgettext_lazy(context="other", message='Your new password has been saved.')


# ALL_GENDERS = ['female', 'male', 'other']
# for gender in ALL_GENDERS:
#     pgettext_lazy(context=gender, message='test1.')
#
# gender = "aaa"
# pgettext_lazy(context=gender, message='test1.')
# pgettext_lazy(context="female1", message='test1.')

# pgettext_lazy(context=self.request.user.get_gender(), message='Your Speedy Net and Speedy Match accounts has been deactivated. You can reactivate them any time.')
#
# pgettext_lazy(context=self.request.user.get_gender(), message='Your {site_name} account has been deactivated. You can reactivate it any time. Your Speedy Net account remains active.').format(site_name=_(current_site.name))
#
# pgettext_lazy(context=self.request.user.get_gender(), message="You've already confirmed this email address.")
#
# pgettext_lazy(context=self.request.user.get_gender(), message="You've confirmed your email address.")
#
# pgettext_lazy(context=self.instance.get_gender(), message='username (slug)')
#
# pgettext_lazy(context=self.instance.get_gender(), message='Save Changes')))
#
# pgettext_lazy(context=self.instance.get_gender(), message="You can't change your username."))
#

pgettext_lazy(context="female", message="You can't change your username.")
pgettext_lazy(context="male", message="You can't change your username.")
pgettext_lazy(context="other", message="You can't change your username.")


# pgettext_lazy(context=self.instance.user.get_gender(), message='Activate your {site_name} account').format(site_name=_(site.name))))
#
# pgettext_lazy(context=self.user.get_gender(), message='Deactivate your {site_name} account').format(site_name=_(site.name)), css_class='btn-danger'))
#
# pgettext_lazy(context=self.defaults['user'].get_gender(), message='Add')))
#
#
