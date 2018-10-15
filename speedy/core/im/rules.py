from rules import predicate, add_perm, is_authenticated

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block


@predicate
def is_participant(user, chat):
    return user.id in (ent.id for ent in chat.participants)


add_perm('im.send_message', is_authenticated & ~is_self & ~there_is_block)
add_perm('im.view_chats', is_authenticated & is_self)
add_perm('im.read_chat', is_authenticated & is_participant)


