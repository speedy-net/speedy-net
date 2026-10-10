"""
Test cases for the permission rules of the messages app of Speedy Core: sending messages, viewing chats and reading chats.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random
        from time import sleep

        from dateutil.relativedelta import relativedelta

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.messages.test.factories import ChatFactory

        from speedy.core.accounts.models import UserEmailAddress
        from speedy.core.blocks.models import Block
        from speedy.core.messages.models import Message


        @only_on_sites_with_login
        class SendMessageRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the rules governing whether a user can send a message to another user (self-messaging, blocking, and rate limits on emails, Discord links and identical messages), run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users, user_1 and user_2.
                _create_users(self, users_count): Creates the given number of additional active users, named user_3, user_4, etc.
                test_cannot_send_message_to_self(self): Asserts a user cannot send a message to himself.
                test_can_send_message_to_other_user(self): Asserts a user can send a message to another user.
                test_cannot_send_message_to_other_user_if_blocked(self): Asserts neither side of a block relationship can send a message to the other.
                test_can_send_message_to_other_user_if_didnt_send_too_many_emails_1(self): Asserts a user whose account is less than 6 hours old can still send up to 4 messages containing an email address and still send messages to other users.
                test_can_send_message_to_other_user_if_didnt_send_too_many_emails_2(self): Asserts sending 5 messages without an email address does not trigger the too-many-emails rule.
                test_cannot_send_message_to_other_user_if_sent_too_many_emails_1(self): Asserts that sending too many messages containing email addresses blocks sending to users not yet messaged, but is lifted once another user replies or the chat is active long enough, and reapplies if another message with an email address is sent and lifted again once the other side replies.
                test_cannot_send_message_to_other_user_if_sent_too_many_emails_2(self): Asserts the too-many-emails restriction is lifted for a user whose account is more than 3 days old once enough other users reply to his messages containing email addresses.
                test_cannot_send_message_to_other_user_if_sent_too_many_emails_3(self): Asserts that a user whose account is 30 days old can send more messages containing email addresses before the too-many-emails restriction is triggered than a newer account.
                test_can_send_message_to_other_user_if_didnt_send_too_many_discord_messages(self): Asserts sending up to 9 messages inviting users to a Discord server does not trigger a restriction.
                test_cannot_send_message_to_other_user_if_sent_too_many_discord_messages(self): Asserts sending a 10th message inviting a new user to a Discord server triggers the too-many-discord-messages restriction on messaging users not yet messaged.
                test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages_1(self): Asserts sending 14 messages with only 2 distinct texts to different users does not trigger the too-many-identical-messages rule.
                test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages_2(self): Asserts a user with a confirmed email address from a common email provider can send more messages with only 2 distinct texts before the too-many-identical-messages rule would apply.
                test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages_3(self): Asserts a user whose account is 60 days old can send more messages with only 2 distinct texts before the too-many-identical-messages rule would apply.
                test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_1(self): Asserts that sending the same message text to too many different users blocks sending to users not yet messaged, and is lifted once enough of those users reply.
                test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_2(self): Asserts a user with a confirmed email address from a common email provider still triggers the too-many-identical-messages restriction after sending the same text to enough users, and the restriction is lifted once enough of those users reply.
                test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_3(self): Asserts a user whose account is 60 days old still triggers the too-many-identical-messages restriction after sending the same text to enough users, and the restriction is lifted once enough of those users reply.
                test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_4(self): Asserts that sending messages alternating between only 2 distinct texts triggers the too-many-identical-messages restriction partway through, and the restriction is lifted once enough recipients reply.
                test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_5(self): Asserts a user with a confirmed email address from a common email provider sending messages alternating between only 2 distinct texts triggers the too-many-identical-messages restriction later than a user without such an email address, and the restriction is lifted once enough recipients reply.
                test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_6(self): Asserts a user whose account is 60 days old sending messages alternating between only 2 distinct texts triggers the too-many-identical-messages restriction later than a newer account, and the restriction is lifted once enough recipients reply.
            """
            def set_up(self):
                """
                Creates two active users, user_1 and user_2, whose accounts are backdated by 10 minutes.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_1.date_created -= relativedelta(hours=0, minutes=10)  # relativedelta(hours=6, minutes=10)
                self.user_1.save_user_and_profile()
                self.user_2.date_created -= relativedelta(hours=0, minutes=10)  # relativedelta(hours=6, minutes=10)
                self.user_2.save_user_and_profile()

            def _create_users(self, users_count):
                """
                Creates the given number of additional active users, backdated by 10 minutes, and assigns them to self as user_3, user_4, etc.

                :param users_count: The number of additional users to create.
                :type users_count: int
                """
                for i in range(users_count):
                    user = ActiveUserFactory()
                    user.date_created -= relativedelta(hours=0, minutes=10)  # relativedelta(hours=6, minutes=10)
                    user.save_user_and_profile()
                    setattr(self, "user_{}".format(3 + i), user)

            def test_cannot_send_message_to_self(self):
                """
                Asserts a user cannot send a message to himself.
                """
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_1), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_1), expr2=False)

            def test_can_send_message_to_other_user(self):
                """
                Asserts a user can send a message to another user.
                """
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)

            def test_cannot_send_message_to_other_user_if_blocked(self):
                """
                Asserts neither side of a block relationship can send a message to the other.
                """
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_2.has_perm(perm='messages.send_message', obj=self.user_1), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_2.has_perm(perm='messages.view_send_message_button', obj=self.user_1), expr2=False)

            def test_can_send_message_to_other_user_if_didnt_send_too_many_emails_1(self):
                """
                Asserts a user whose account is more than 3 days old can send 4 messages containing an email address and still send a message to a user not yet messaged.
                """
                self._create_users(users_count=6)
                self.user_1.date_created -= relativedelta(days=3, minutes=10)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(4):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_can_send_message_to_other_user_if_didnt_send_too_many_emails_2(self):
                """
                Asserts sending 5 messages without an email address, each to a different user, does not trigger the too-many-emails restriction.
                """
                self._create_users(users_count=6)
                chats = dict()
                for i in range(5):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_emails_1(self):
                """
                Asserts that a user whose account is more than 3 days old is blocked from messaging a user not yet messaged after sending 5 messages containing email addresses, that the restriction is lifted once another messaged user replies, and that it reapplies after another message with an email address is sent and is lifted again once the other side replies.
                """
                self._create_users(users_count=6)
                self.user_1.date_created -= relativedelta(days=3, minutes=10)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(5):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                Message.objects.send_message(from_entity=self.user_7, chat=chats[str(4)], text='Lorem ipsum dolor sit amet!')
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                chats[str(5)] = ChatFactory(ent1=self.user_1, ent2=self.user_8)
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(5)], text='Lorem ipsum dolor sit amet!')
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(5)], text='hello@example.org')
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                Message.objects.send_message(from_entity=self.user_8, chat=chats[str(5)], text='Hi.')
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_emails_2(self):
                """
                Asserts that a user whose account is more than 3 days old is blocked from messaging a user not yet messaged after sending email-containing messages to 19 different users, and that the restriction is lifted only once most of those 19 users reply (replies from just 4 of them are not enough).
                """
                self._create_users(users_count=20)
                self.user_1.date_created -= relativedelta(days=3, minutes=10)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(4):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(15):
                    chats[str(4 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(4 + 3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(4 + i)], text='test@example.com')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(4):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(3 + i)), chat=chats[str(i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(12):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(4 + 3 + i)), chat=chats[str(4 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_emails_3(self):
                """
                Asserts that a user whose account is 30 days old can send email-containing messages to 19 different users without triggering the too-many-emails restriction, but sending to 5 more (24 total) triggers it for users not yet messaged.
                """
                self._create_users(users_count=30)
                self.user_1.date_created -= relativedelta(days=30)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(19):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='test@example.com')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(5):
                    chats[str(19 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(19 + 3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(19 + i)], text='test@example.com')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_can_send_message_to_other_user_if_didnt_send_too_many_discord_messages(self):
                """
                Asserts sending 9 messages inviting different users to join a Discord server does not trigger the too-many-discord-messages restriction.
                """
                self._create_users(users_count=11)
                chats = dict()
                for i in range(9):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Join our discord server!')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_discord_messages(self):
                """
                Asserts that sending a 10th message inviting a new user to join a Discord server triggers the too-many-discord-messages restriction on messaging users not yet messaged.
                """
                self._create_users(users_count=11)
                chats = dict()
                for i in range(9):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Join our discord server!')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                chats[str(9)] = ChatFactory(ent1=self.user_1, ent2=self.user_12)
                Message.objects.send_message(from_entity=self.user_1, chat=chats[str(9)], text='Join our discord server!')
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages_1(self):
                """
                Asserts sending 14 messages that alternate between only 2 distinct texts, each to a different user, does not trigger the too-many-identical-messages restriction.
                """
                self._create_users(users_count=24)
                chats = dict()
                for i in range(14):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet {}'.format(i % 2))
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages_2(self):
                """
                Asserts a user with a confirmed primary email address from a common email provider can send 28 messages that alternate between only 2 distinct texts without triggering the too-many-identical-messages restriction.
                """
                self._create_users(users_count=38)
                user_1_email_address = UserEmailAddress(user=self.user_1, email='1@{}'.format(random.choice(['gmail.com', 'yahoo.com', 'icloud.com'])), is_confirmed=True)
                user_1_email_address.make_primary()
                chats = dict()
                for i in range(28):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet {}'.format(i % 2))
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_can_send_message_to_other_user_if_didnt_send_too_many_identical_messages_3(self):
                """
                Asserts a user whose account is 60 days old can send 40 messages that alternate between only 2 distinct texts without triggering the too-many-identical-messages restriction.
                """
                self._create_users(users_count=50)
                self.user_1.date_created -= relativedelta(days=60, minutes=10)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(40):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet {}'.format(i % 2))
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_1(self):
                """
                Asserts that sending the exact same message text to 18 different users triggers the too-many-identical-messages restriction on messaging users not yet messaged, and that the restriction is lifted once the last 11 of those recipients reply.
                """
                self._create_users(users_count=28)
                chats = dict()
                for i in range(7):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(11):
                    chats[str(7 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(7 + 3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(7 + i)], text='Lorem ipsum dolor sit amet')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(11):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(7 + 3 + i)), chat=chats[str(7 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_2(self):
                """
                Asserts that a user with a confirmed primary email address from a common email provider can send the exact same message text to 14 different users before 11 more (25 total) trigger the too-many-identical-messages restriction, which is then lifted once the last 11 recipients reply.
                """
                self._create_users(users_count=35)
                user_1_email_address = UserEmailAddress(user=self.user_1, email='1@{}'.format(random.choice(['gmail.com', 'yahoo.com', 'icloud.com'])), is_confirmed=True)
                user_1_email_address.make_primary()
                chats = dict()
                for i in range(14):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(11):
                    chats[str(14 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(14 + 3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(14 + i)], text='Lorem ipsum dolor sit amet')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(11):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(14 + 3 + i)), chat=chats[str(14 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_3(self):
                """
                Asserts that a user whose account is 60 days old can send the exact same message text to 29 different users before 11 more (40 total) trigger the too-many-identical-messages restriction, which is then lifted once the last 11 recipients reply.
                """
                self._create_users(users_count=50)
                self.user_1.date_created -= relativedelta(days=60, minutes=10)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(29):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(11):
                    chats[str(29 + i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(29 + 3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(29 + i)], text='Lorem ipsum dolor sit amet')
                    sleep(0.01)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(11):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(29 + 3 + i)), chat=chats[str(29 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_4(self):
                """
                Asserts that sending 34 messages alternating between only 2 distinct texts to different users triggers the too-many-identical-messages restriction starting from the 15th message and keeps it in effect through all 34, and that the restriction is lifted once the last 20 of those recipients reply.
                """
                self._create_users(users_count=44)
                chats = dict()
                for i in range(34):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet {}'.format(i % 2))
                    sleep(0.01)
                    if (i < 14):
                        self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    else:
                        self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(20):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(10 + 3 + i)), chat=chats[str(10 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_5(self):
                """
                Asserts that a user with a confirmed primary email address from a common email provider sending 40 messages alternating between only 2 distinct texts triggers the too-many-identical-messages restriction starting later, from the 29th message, than a user without such an email address, and that the restriction is lifted once the last 20 recipients reply.
                """
                self._create_users(users_count=50)
                user_1_email_address = UserEmailAddress(user=self.user_1, email='1@{}'.format(random.choice(['gmail.com', 'yahoo.com', 'icloud.com'])), is_confirmed=True)
                user_1_email_address.make_primary()
                chats = dict()
                for i in range(40):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet {}'.format(i % 2))
                    sleep(0.01)
                    if (i < 28):
                        self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    else:
                        self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(20):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(10 + 3 + i)), chat=chats[str(10 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)

            def test_cannot_send_message_to_other_user_if_sent_too_many_identical_messages_6(self):
                """
                Asserts that a user whose account is 60 days old sending 70 messages alternating between only 2 distinct texts triggers the too-many-identical-messages restriction starting later, from the 59th message, than a newer account, and that the restriction is lifted once the last 20 recipients reply.
                """
                self._create_users(users_count=80)
                self.user_1.date_created -= relativedelta(days=60, minutes=10)
                self.user_1.save_user_and_profile()
                chats = dict()
                for i in range(70):
                    chats[str(i)] = ChatFactory(ent1=self.user_1, ent2=getattr(self, "user_{}".format(3 + i)))
                    Message.objects.send_message(from_entity=self.user_1, chat=chats[str(i)], text='Lorem ipsum dolor sit amet {}'.format(i % 2))
                    sleep(0.01)
                    if (i < 58):
                        self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                    else:
                        self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                    self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=False)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)
                for i in range(20):
                    Message.objects.send_message(from_entity=getattr(self, "user_{}".format(10 + 3 + i)), chat=chats[str(10 + i)], text='Lorem ipsum dolor sit amet!')
                    sleep(0.01)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.send_message', obj=self.user_3), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_2), expr2=True)
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_send_message_button', obj=self.user_3), expr2=True)


        @only_on_sites_with_login
        class ViewChatsRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the rules governing whether a user can view a list of chats belonging to a given user, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two active users, user_1 and user_2.
                test_can_see_his_chats(self): Asserts a user can view his own list of chats.
                test_cannot_see_other_user_chats(self): Asserts a user cannot view another user's list of chats.
            """
            def set_up(self):
                """
                Creates two active users, user_1 and user_2.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()

            def test_can_see_his_chats(self):
                """
                Asserts a user can view his own list of chats.
                """
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_chats', obj=self.user_1), expr2=True)

            def test_cannot_see_other_user_chats(self):
                """
                Asserts a user cannot view another user's list of chats.
                """
                self.assertIs(expr1=self.user_1.has_perm(perm='messages.view_chats', obj=self.user_2), expr2=False)


        @only_on_sites_with_login
        class ReadChatRulesOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the rules governing whether a user can read a chat, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates three active users and two chats, one between user_1 and user_2, and another between user_1 and user_3.
                test_can_read_his_chat(self): Asserts a user can read a chat he participates in.
                test_cannot_read_a_chat_user_is_not_participate_in(self): Asserts a user cannot read a chat he does not participate in.
            """
            def set_up(self):
                """
                Creates three active users and two chats, one between user_1 and user_2, and another between user_1 and user_3.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.chat_1_2 = ChatFactory(ent1=self.user_1, ent2=self.user_2)
                self.chat_1_3 = ChatFactory(ent1=self.user_1, ent2=self.user_3)

            def test_can_read_his_chat(self):
                """
                Asserts a user can read a chat he participates in.
                """
                self.assertIs(expr1=self.user_2.has_perm(perm='messages.read_chat', obj=self.chat_1_2), expr2=True)

            def test_cannot_read_a_chat_user_is_not_participate_in(self):
                """
                Asserts a user cannot read a chat he does not participate in.
                """
                self.assertIs(expr1=self.user_2.has_perm(perm='messages.read_chat', obj=self.chat_1_3), expr2=False)


