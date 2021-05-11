import logging
from datetime import timedelta

from rules import predicate, add_perm, is_authenticated
from django.contrib.sites.models import Site
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block
from speedy.core.messages.models import Chat

logger = logging.getLogger(__name__)


@predicate
def is_participant(user, chat):
    return user.id in (ent.id for ent in chat.participants)


@predicate
def can_send_new_message(user):
    """
    If the user signed up to Speedy Net less than 10 days ago,
    and sent at least 5 messages with an email address without a reply in the last day,
    or at least 10 messages with an email address without a reply in the last 3 days,
    or at least 15 messages with an email address without a reply in the last week,
    then don't let them send any new messages to new chats.
    """
    if ((now() - user.date_created).days < 10):
        limit_user_messages_1_day = 5
        limit_user_messages_3_days = 10
        limit_user_messages_7_days = 15
    else:
        limit_user_messages_1_day = 20
        limit_user_messages_3_days = 60
        limit_user_messages_7_days = 60
    count_user_messages_1_day = max(
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="@",
            created_after=now() - timedelta(days=1),
        ),
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="http://",
            created_after=now() - timedelta(days=1),
        ),
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="https://",
            created_after=now() - timedelta(days=1),
        ),
    )
    count_user_messages_3_days = max(
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="@",
            created_after=now() - timedelta(days=3),
        ),
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="http://",
            created_after=now() - timedelta(days=3),
        ),
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="https://",
            created_after=now() - timedelta(days=3),
        ),
    )
    count_user_messages_7_days = max(
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="@",
            created_after=now() - timedelta(days=7),
        ),
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="http://",
            created_after=now() - timedelta(days=7),
        ),
        Chat.objects.count_chats_with_string_in_messages_and_only_one_sender(
            entity=user,
            string_in_messages="https://",
            created_after=now() - timedelta(days=7),
        ),
    )
    if ((count_user_messages_1_day >= limit_user_messages_1_day) or (count_user_messages_3_days >= limit_user_messages_3_days) or (count_user_messages_7_days >= limit_user_messages_7_days)):
        site = Site.objects.get_current()
        logger.warning("User {user} can't send messages today on {site_name} ({count_user_messages_1_day} / {count_user_messages_3_days} / {count_user_messages_7_days}, registered {registered_days_ago} days ago).".format(
            user=user,
            site_name=_(site.name),
            count_user_messages_1_day=count_user_messages_1_day,
            count_user_messages_3_days=count_user_messages_3_days,
            count_user_messages_7_days=count_user_messages_7_days,
            registered_days_ago=(now() - user.date_created).days,
        ))
        return False
    return True


@predicate
def can_send_message(user, other_user):
    existing_chat = Chat.objects.chat_with(ent1=user, ent2=other_user, create=False)
    if (existing_chat is not None):
        return True
    else:
        return can_send_new_message(user=user)


add_perm('messages.view_send_message_button', is_authenticated & ~is_self & ~there_is_block)
add_perm('messages.send_message', is_authenticated & ~is_self & ~there_is_block & can_send_message)
add_perm('messages.view_chats', is_authenticated & is_self)
add_perm('messages.read_chat', is_authenticated & is_participant)


