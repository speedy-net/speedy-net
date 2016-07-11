from rules import predicate, add_perm, is_authenticated


@predicate
def is_self(user, other):
    return user == other


add_perm('uploads.upload', is_authenticated & is_self)
