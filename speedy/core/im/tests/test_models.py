from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login

    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.im.test.factories import ChatFactory


    @only_on_sites_with_login
    class ChatTestCase(SiteTestCase):
        def get_active_user_doron(self):
            user = ActiveUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon")
            user.save_user_and_profile()
            return user

        def get_active_user_jennifer(self):
            user = ActiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly")
            user.save_user_and_profile()
            return user

        def test_id_length(self):
            chat = ChatFactory()
            self.assertEqual(first=len(chat.id), second=20)

        def test_str_private_chat(self):
            user_1 = self.get_active_user_doron()
            user_2 = self.get_active_user_jennifer()
            chat = ChatFactory(ent1=user_1, ent2=user_2)
            if (self.site.id == django_settings.SPEEDY_MATCH_SITE_ID):
                self.assertEqual(first=str(chat), second='Doron, Jennifer')
            else:
                self.assertEqual(first=str(chat), second="Doron Matalon, Jennifer Connelly")

        def test_get_slug_private_chat(self):
            user_1 = self.get_active_user_doron()
            user_2 = self.get_active_user_jennifer()
            chat = ChatFactory(ent1=user_1, ent2=user_2)
            self.assertEqual(first=chat.get_slug(current_user=user_1), second=user_2.slug)
            self.assertEqual(first=chat.get_slug(current_user=user_2), second=user_1.slug)
            self.assertNotEqual(first=chat.get_slug(current_user=user_1), second=user_1.slug)
            self.assertNotEqual(first=chat.get_slug(current_user=user_2), second=user_2.slug)
            self.assertEqual(first=chat.get_slug(current_user=user_1), second="jennifer-connelly")
            self.assertEqual(first=chat.get_slug(current_user=user_2), second="doron-matalon")

        def test_str_group_chat(self):
            user_1 = self.get_active_user_doron()
            user_2 = self.get_active_user_jennifer()
            user_3 = ActiveUserFactory()
            user_4 = ActiveUserFactory()
            chat = ChatFactory(ent1=None, ent2=None, is_group=True, group=[user_1, user_2, user_3, user_4])
            # print("test_str_group_chat: str(chat)=", str(chat)) #### ~~~~ TODO: remove this line!
            self.assertEqual(first=str(chat), second="{}, {}, {}, {}".format(user_1.profile.get_name(), user_2.profile.get_name(), user_3.profile.get_name(), user_4.profile.get_name()))
            self.assertEqual(first=str(chat), second="{}, {}, {}, {}".format(str(user_1), str(user_2), str(user_3), str(user_4)))
            if (self.site.id == django_settings.SPEEDY_MATCH_SITE_ID):
                self.assertEqual(first=str(chat), second="Doron, Jennifer, {}, {}".format(user_3.profile.get_name(), user_4.profile.get_name()))
            else:
                self.assertEqual(first=str(chat), second="Doron Matalon, Jennifer Connelly, {}, {}".format(user_3.profile.get_name(), user_4.profile.get_name()))

        def test_get_slug_group_chat(self):
            user_1 = self.get_active_user_doron()
            user_2 = self.get_active_user_jennifer()
            user_3 = ActiveUserFactory()
            user_4 = ActiveUserFactory()
            chat = ChatFactory(ent1=None, ent2=None, is_group=True, group=[user_1, user_2, user_3, user_4])
            self.assertEqual(first=chat.get_slug(current_user=user_1), second=chat.id)


