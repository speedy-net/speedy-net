from rules import predicate, add_perm, is_authenticated

from speedy.net.blocks.rules import is_blocked, has_blocked


@predicate
def is_self(user, other):
    return user == other


@predicate
def is_participant(user, chat):
    return user.id in (ent.id for ent in chat.participants)


add_perm('im.send_message', is_authenticated & ~is_self & ~is_blocked & ~has_blocked)
add_perm('im.view_chats', is_authenticated & is_self)
add_perm('im.read_chat', is_authenticated & is_participant)
