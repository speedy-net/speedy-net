import logging
from datetime import timedelta

from rules import predicate, add_perm, is_authenticated
from django.contrib.sites.models import Site
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _

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

    If the user sent more than 30 identical messages without a reply,
    then don't let them send any new messages to new chats.

    If the user signed up to Speedy Net less than 6 hours ago, and they don't use a gmail.com email address,
    then don't let them send any new messages to new chats.
    """
    can_send = True
    language_code = get_language()
    if (language_code == 'en'):
        if (user.date_created >= (now() - timedelta(minutes=360))):
            can_send = False
            if (user.has_confirmed_email):
                emails = user.email_addresses.filter(is_primary=True)
                if ((len(emails) == 1) and (user.email) and (user.email == emails[0].email) and (emails[0].is_confirmed)):
                    email_name, domain_part = user.email.strip().rsplit("@", 1)
                    if (domain_part in {'gmail.com'}):
                        can_send = True
        if ((now() - user.date_created).days < 7):
            if (user.has_confirmed_email):
                emails = user.email_addresses.filter(is_primary=True)
                if ((len(emails) == 1) and (user.email) and (user.email == emails[0].email) and (emails[0].is_confirmed)):
                    email_name, domain_part = user.email.strip().rsplit("@", 1)
                    if (domain_part in {'outlook.com', 'hotmail.com'}):
                        can_send = False
    if ((now() - user.date_created).days < 10):
        limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 5, 10, 15
        if ((now() - user.date_created).days < 3):
            limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 2, 10, 15
            if (user.has_confirmed_email):
                emails = user.email_addresses.filter(is_primary=True)
                if ((len(emails) == 1) and (user.email) and (user.email == emails[0].email) and (emails[0].is_confirmed)):
                    email_name, domain_part = user.email.strip().rsplit("@", 1)
                    if (domain_part in {'gmail.com'}):
                        if ((now() - user.date_created).days < 2):
                            limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 3, 10, 15
                        else:
                            limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 5, 10, 15
    else:
        limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 20, 60, 60
    strings_in_messages = ["@", "http://", "https://"]
    count_user_messages_1_day = Chat.objects.count_chats_with_strings_in_messages_and_only_one_sender(
        entity=user,
        strings_in_messages=strings_in_messages,
        created_after=now() - timedelta(days=1),
    )
    count_user_messages_3_days = Chat.objects.count_chats_with_strings_in_messages_and_only_one_sender(
        entity=user,
        strings_in_messages=strings_in_messages,
        created_after=now() - timedelta(days=3),
    )
    count_user_messages_7_days = Chat.objects.count_chats_with_strings_in_messages_and_only_one_sender(
        entity=user,
        strings_in_messages=strings_in_messages,
        created_after=now() - timedelta(days=7),
    )
    if ((count_user_messages_1_day >= limit_user_messages_1_day) or (count_user_messages_3_days >= limit_user_messages_3_days) or (count_user_messages_7_days >= limit_user_messages_7_days)):
        site = Site.objects.get_current()
        language_code = get_language()
        logger.warning("[count_user_messages] User {user} can't send messages today on {site_name} ({count_user_messages_1_day} / {count_user_messages_3_days} / {count_user_messages_7_days}, registered {registered_days_ago} days ago), language_code={language_code}.".format(
            user=user,
            site_name=_(site.name),
            count_user_messages_1_day=count_user_messages_1_day,
            count_user_messages_3_days=count_user_messages_3_days,
            count_user_messages_7_days=count_user_messages_7_days,
            registered_days_ago=(now() - user.date_created).days,
            language_code=language_code,
        ))
        can_send = False
    if ((now() - user.date_created).days < 15):
        limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 10, 100, 100
    else:
        limit_user_messages_1_day, limit_user_messages_3_days, limit_user_messages_7_days = 15, 100, 100
    strings_in_messages = ["discord"]
    count_user_messages_1_day = Chat.objects.count_chats_with_strings_in_messages_and_only_one_sender(
        entity=user,
        strings_in_messages=strings_in_messages,
        created_after=now() - timedelta(days=1),
    )
    count_user_messages_3_days = Chat.objects.count_chats_with_strings_in_messages_and_only_one_sender(
        entity=user,
        strings_in_messages=strings_in_messages,
        created_after=now() - timedelta(days=3),
    )
    count_user_messages_7_days = Chat.objects.count_chats_with_strings_in_messages_and_only_one_sender(
        entity=user,
        strings_in_messages=strings_in_messages,
        created_after=now() - timedelta(days=7),
    )
    if ((count_user_messages_1_day >= limit_user_messages_1_day) or (count_user_messages_3_days >= limit_user_messages_3_days) or (count_user_messages_7_days >= limit_user_messages_7_days)):
        site = Site.objects.get_current()
        language_code = get_language()
        logger.warning("[count_user_messages] User {user} can't send messages today on {site_name} ({count_user_messages_1_day} / {count_user_messages_3_days} / {count_user_messages_7_days}, registered {registered_days_ago} days ago), language_code={language_code}.".format(
            user=user,
            site_name=_(site.name),
            count_user_messages_1_day=count_user_messages_1_day,
            count_user_messages_3_days=count_user_messages_3_days,
            count_user_messages_7_days=count_user_messages_7_days,
            registered_days_ago=(now() - user.date_created).days,
            language_code=language_code,
        ))
        can_send = False
    limit_identical_messages = 8
    if ((now() - user.date_created).days < 60):
        if (user.has_confirmed_email):
            emails = user.email_addresses.filter(is_primary=True)
            if ((len(emails) == 1) and (user.email) and (user.email == emails[0].email) and (emails[0].is_confirmed)):
                email_name, domain_part = user.email.strip().rsplit("@", 1)
                if (domain_part in {'gmail.com', 'yahoo.com', 'icloud.com', 'outlook.com', 'hotmail.com'}):
                    limit_identical_messages = 15
    else:
        if (user.has_confirmed_email):
            limit_identical_messages = 30
        else:
            limit_identical_messages = 15
    count_identical_messages_in_chats = Chat.objects.count_identical_messages_in_chats_with_only_one_sender(
        entity=user,
    )
    if (count_identical_messages_in_chats[0] >= limit_identical_messages):
        site = Site.objects.get_current()
        language_code = get_language()
        logger.warning("[count_identical_messages] User {user} can't send messages today on {site_name} ({count_identical_messages_in_chats_0} / \"{count_identical_messages_in_chats_1}\", registered {registered_days_ago} days ago), language_code={language_code}.".format(
            user=user,
            site_name=_(site.name),
            count_identical_messages_in_chats_0=count_identical_messages_in_chats[0],
            count_identical_messages_in_chats_1=count_identical_messages_in_chats[1],
            registered_days_ago=(now() - user.date_created).days,
            language_code=language_code,
        ))
        can_send = False
    return can_send


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


