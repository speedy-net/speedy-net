from rules import predicate


@predicate
def is_self(user, other_user):
    return user == other_user


@predicate
def is_active(user, other_user):
    return (other_user.profile.is_active)


