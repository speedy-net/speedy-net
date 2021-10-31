# This file is only for ./make_all_messages.sh, it is not used otherwise.

from django.utils.translation import gettext_lazy as _, ngettext_lazy, pgettext_lazy


_('My height in centimeters')


pgettext_lazy(context="female", message='Add profile picture')
pgettext_lazy(context="male", message='Add profile picture')
pgettext_lazy(context="other", message='Add profile picture')

pgettext_lazy(context="female", message='My height in centimeters')
pgettext_lazy(context="male", message='My height in centimeters')
pgettext_lazy(context="other", message='My height in centimeters')

pgettext_lazy(context="female", message='My ideal match')
pgettext_lazy(context="male", message='My ideal match')
pgettext_lazy(context="other", message='My ideal match')

pgettext_lazy(context="female", message='Minimal age to match')
pgettext_lazy(context="male", message='Minimal age to match')
pgettext_lazy(context="other", message='Minimal age to match')

pgettext_lazy(context="female", message='Maximal age to match')
pgettext_lazy(context="male", message='Maximal age to match')
pgettext_lazy(context="other", message='Maximal age to match')

pgettext_lazy(context="female", message="Please write a few words about yourself.")
pgettext_lazy(context="male", message="Please write a few words about yourself.")
pgettext_lazy(context="other", message="Please write a few words about yourself.")

pgettext_lazy(context="female", message="Do you have children? How many?")
pgettext_lazy(context="male", message="Do you have children? How many?")
pgettext_lazy(context="other", message="Do you have children? How many?")

pgettext_lazy(context="female", message="Do you want (more) children?")
pgettext_lazy(context="male", message="Do you want (more) children?")
pgettext_lazy(context="other", message="Do you want (more) children?")

pgettext_lazy(context="female", message="Who is your ideal partner?")
pgettext_lazy(context="male", message="Who is your ideal partner?")
pgettext_lazy(context="other", message="Who is your ideal partner?")

pgettext_lazy(context="female", message="We're sorry, but you are not authorized to use the {site_name} website. We have found that some of the information you provided when registering on the site is incorrect or that you have violated the rules of use of the site. Therefore you are not authorized to use the site.")
pgettext_lazy(context="male", message="We're sorry, but you are not authorized to use the {site_name} website. We have found that some of the information you provided when registering on the site is incorrect or that you have violated the rules of use of the site. Therefore you are not authorized to use the site.")
pgettext_lazy(context="other", message="We're sorry, but you are not authorized to use the {site_name} website. We have found that some of the information you provided when registering on the site is incorrect or that you have violated the rules of use of the site. Therefore you are not authorized to use the site.")


