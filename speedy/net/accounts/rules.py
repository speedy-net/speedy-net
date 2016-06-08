from rules import predicate, add_perm


@predicate
def is_email_address_owner(user, email_address):
    return user.id == email_address.user_id


@predicate
def email_address_is_confirmed(user, email_address):
    return email_address.is_confirmed


@predicate
def email_address_is_primary(user, email_address):
    return email_address.is_primary


add_perm('accounts.confirm_useremailaddress', is_email_address_owner & ~email_address_is_confirmed)
add_perm('accounts.delete_useremailaddress', is_email_address_owner & ~email_address_is_primary)
add_perm('accounts.setprimary_useremailaddress', is_email_address_owner & email_address_is_confirmed)
