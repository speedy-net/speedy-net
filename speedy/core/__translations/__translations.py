# This file is only for ./make_all_messages.sh, it is not used otherwise.

from django.utils.translation import gettext_lazy as _, ngettext_lazy, pgettext_lazy


# from django
_('Enter a valid email address.')
_("Email address")
_("email address")
_("Email address:")
_("Email")
_("Value must be valid JSON.")
_("Please enter a correct %(username)s and password. Note that both fields may be case-sensitive.")


# from friendship.models
_('Message')

_('Friendship Request')
_('Friendship Requests')

_('Friend')
_('Friends')

_('Following Relationship')
_('Following Relationships')

_('Blocker Relationship')
_('Blocked Relationships')


# from django
ngettext_lazy(
    singular='List contains %(show_value)d item, it should contain no more than %(limit_value)d.',
    plural='List contains %(show_value)d items, it should contain no more than %(limit_value)d.',
    number='limit_value'
)


# from speedy.core
pgettext_lazy(context="female", message='username (slug)')
pgettext_lazy(context="male", message='username (slug)')
pgettext_lazy(context="other", message='username (slug)')

pgettext_lazy(context="female", message='Save Changes')
pgettext_lazy(context="male", message='Save Changes')
pgettext_lazy(context="other", message='Save Changes')

pgettext_lazy(context="female", message="You can't change your username.")
pgettext_lazy(context="male", message="You can't change your username.")
pgettext_lazy(context="other", message="You can't change your username.")

pgettext_lazy(context="female", message='Activate your {site_name} account')
pgettext_lazy(context="male", message='Activate your {site_name} account')
pgettext_lazy(context="other", message='Activate your {site_name} account')

pgettext_lazy(context="female", message='Deactivate your {site_name} account')
pgettext_lazy(context="male", message='Deactivate your {site_name} account')
pgettext_lazy(context="other", message='Deactivate your {site_name} account')

pgettext_lazy(context="female", message='Add')
pgettext_lazy(context="male", message='Add')
pgettext_lazy(context="other", message='Add')

pgettext_lazy(context="female", message="Vegan (eats only plants and fungi)")
pgettext_lazy(context="male", message="Vegan (eats only plants and fungi)")
pgettext_lazy(context="other", message="Vegan (eats only plants and fungi)")

pgettext_lazy(context="female", message="Vegetarian (doesn't eat fish and meat)")
pgettext_lazy(context="male", message="Vegetarian (doesn't eat fish and meat)")
pgettext_lazy(context="other", message="Vegetarian (doesn't eat fish and meat)")

pgettext_lazy(context="female", message="Carnist (eats animals)")
pgettext_lazy(context="male", message="Carnist (eats animals)")
pgettext_lazy(context="other", message="Carnist (eats animals)")

pgettext_lazy(context="female", message='Vegan'),
pgettext_lazy(context="male", message='Vegan'),
pgettext_lazy(context="other", message='Vegan'),

pgettext_lazy(context="female", message='Vegetarian'),
pgettext_lazy(context="male", message='Vegetarian'),
pgettext_lazy(context="other", message='Vegetarian'),

pgettext_lazy(context="female", message='Carnist'),
pgettext_lazy(context="male", message='Carnist'),
pgettext_lazy(context="other", message='Carnist'),

pgettext_lazy(context="female", message="No")
pgettext_lazy(context="male", message="No")
pgettext_lazy(context="other", message="No")

pgettext_lazy(context="female", message="Sometimes")
pgettext_lazy(context="male", message="Sometimes")
pgettext_lazy(context="other", message="Sometimes")

pgettext_lazy(context="female", message="Yes")
pgettext_lazy(context="male", message="Yes")
pgettext_lazy(context="other", message="Yes")

pgettext_lazy(context="female", message="Single")
pgettext_lazy(context="male", message="Single")
pgettext_lazy(context="other", message="Single")

pgettext_lazy(context="female", message="Divorced")
pgettext_lazy(context="male", message="Divorced")
pgettext_lazy(context="other", message="Divorced")

pgettext_lazy(context="female", message="Widowed")
pgettext_lazy(context="male", message="Widowed")
pgettext_lazy(context="other", message="Widowed")

pgettext_lazy(context="female", message="In a relationship")
pgettext_lazy(context="male", message="In a relationship")
pgettext_lazy(context="other", message="In a relationship")

pgettext_lazy(context="female", message="In an open relationship")
pgettext_lazy(context="male", message="In an open relationship")
pgettext_lazy(context="other", message="In an open relationship")

pgettext_lazy(context="female", message="It's complicated")
pgettext_lazy(context="male", message="It's complicated")
pgettext_lazy(context="other", message="It's complicated")

pgettext_lazy(context="female", message="Separated")
pgettext_lazy(context="male", message="Separated")
pgettext_lazy(context="other", message="Separated")

pgettext_lazy(context="female", message="Married")
pgettext_lazy(context="male", message="Married")
pgettext_lazy(context="other", message="Married")

pgettext_lazy(context="female", message='Your new password has been saved.')
pgettext_lazy(context="male", message='Your new password has been saved.')
pgettext_lazy(context="other", message='Your new password has been saved.')

pgettext_lazy(context="female", message='Your Speedy Net and Speedy Match accounts has been deactivated. You can reactivate them any time.')
pgettext_lazy(context="male", message='Your Speedy Net and Speedy Match accounts has been deactivated. You can reactivate them any time.')
pgettext_lazy(context="other", message='Your Speedy Net and Speedy Match accounts has been deactivated. You can reactivate them any time.')

pgettext_lazy(context="female", message='Your {site_name} account has been deactivated. You can reactivate it any time. Your Speedy Net account remains active.')
pgettext_lazy(context="male", message='Your {site_name} account has been deactivated. You can reactivate it any time. Your Speedy Net account remains active.')
pgettext_lazy(context="other", message='Your {site_name} account has been deactivated. You can reactivate it any time. Your Speedy Net account remains active.')

pgettext_lazy(context="female", message="You've already confirmed this email address.")
pgettext_lazy(context="male", message="You've already confirmed this email address.")
pgettext_lazy(context="other", message="You've already confirmed this email address.")

pgettext_lazy(context="female", message="You've confirmed your email address.")
pgettext_lazy(context="male", message="You've confirmed your email address.")
pgettext_lazy(context="other", message="You've confirmed your email address.")

pgettext_lazy(context="female", message='Send')
pgettext_lazy(context="male", message='Send')
pgettext_lazy(context="other", message='Send')

pgettext_lazy(context="female", message="You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed.")
pgettext_lazy(context="male", message="You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed.")
pgettext_lazy(context="other", message="You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed.")

pgettext_lazy(context="female", message="This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.")
pgettext_lazy(context="male", message="This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.")
pgettext_lazy(context="other", message="This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.")

pgettext_lazy(context="female", message="You cannot be friends with yourself.")
pgettext_lazy(context="male", message="You cannot be friends with yourself.")
pgettext_lazy(context="other", message="You cannot be friends with yourself.")

pgettext_lazy(context="female", message="You already requested friendship from this user.")
pgettext_lazy(context="male", message="You already requested friendship from this user.")
pgettext_lazy(context="other", message="You already requested friendship from this user.")

pgettext_lazy(context="female", message="You already are friends with this user.")
pgettext_lazy(context="male", message="You already are friends with this user.")
pgettext_lazy(context="other", message="You already are friends with this user.")

pgettext_lazy(context="female", message="You've cancelled your friend request.")
pgettext_lazy(context="male", message="You've cancelled your friend request.")
pgettext_lazy(context="other", message="You've cancelled your friend request.")

pgettext_lazy(context="female", message="You have removed this user from friends.")
pgettext_lazy(context="male", message="You have removed this user from friends.")
pgettext_lazy(context="other", message="You have removed this user from friends.")

pgettext_lazy(context="female", message='Welcome to {site_name}!')
pgettext_lazy(context="male", message='Welcome to {site_name}!')
pgettext_lazy(context="other", message='Welcome to {site_name}!')

pgettext_lazy(context="female", message='Friends')
pgettext_lazy(context="male", message='Friends')
pgettext_lazy(context="other", message='Friends')


