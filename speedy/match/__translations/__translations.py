# This file is only for ./make_all_messages.sh, it is not used otherwise.

from django.utils.translation import gettext_lazy as _, ngettext_lazy, pgettext_lazy


pgettext_lazy(context="female", message='Add profile picture')
pgettext_lazy(context="male", message='Add profile picture')
pgettext_lazy(context="other", message='Add profile picture')

pgettext_lazy(context="female", message='Do you want (more) children?')
pgettext_lazy(context="male", message='Do you want (more) children?')
pgettext_lazy(context="other", message='Do you want (more) children?')

pgettext_lazy(context="female", message='My ideal match')
pgettext_lazy(context="male", message='My ideal match')
pgettext_lazy(context="other", message='My ideal match')

pgettext_lazy(context="female", message='Minimal age to match')
pgettext_lazy(context="male", message='Minimal age to match')
pgettext_lazy(context="other", message='Minimal age to match')

pgettext_lazy(context="female", message='Maximal age to match')
pgettext_lazy(context="male", message='Maximal age to match')
pgettext_lazy(context="other", message='Maximal age to match')


