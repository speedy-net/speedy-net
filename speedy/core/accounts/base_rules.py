from rules import predicate


@predicate
def is_self(user, other_user):
    return user == other_user


