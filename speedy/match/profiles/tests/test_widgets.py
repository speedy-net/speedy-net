"""
Test cases for the profile widgets used on Speedy Match: the user rank widget, the user extra details widget and the Speedy Net user widget.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test.client import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from django.utils.translation import gettext_lazy as _

        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.match.accounts.test.user_factories import ActiveUserFactory, SpeedyNetInactiveUserFactory

        from speedy.core.accounts.models import User
        from speedy.core.blocks.models import Block
        from speedy.match.profiles.widgets import UserRankWidget, UserExtraDetailsWidget
        from speedy.net.profiles.widgets import UserOnSpeedyNetWidget


        class WidgetTestCaseMixin(object):
            """
            Mixin for widget test cases, creating a request factory and a helper to build a widget for a viewer and a user.

            Methods:
                set_up(self): Creates a request factory, an active user and another active user (the viewer).
                get_widget(self, widget_class, viewer, user=None): Creates a widget of the given class, for the given viewer and user.
            """

            def set_up(self):
                """
                Creates a request factory, an active user and another active user (the viewer).
                """
                super().set_up()
                self.factory = RequestFactory()
                self.user = ActiveUserFactory()
                self.viewer = ActiveUserFactory()

            def get_widget(self, widget_class, viewer, user=None):
                """
                Creates a widget of the given class, for the given viewer and user.

                :param widget_class: The widget class.
                :type widget_class: type
                :param viewer: The entity viewing the profile.
                :type viewer: speedy.core.accounts.models.Entity
                :param user: The user whose profile the widget belongs to. Defaults to self.user.
                :type user: speedy.core.accounts.models.User
                :return: The widget.
                :rtype: speedy.core.profiles.widgets.Widget
                """
                request = self.factory.get('/')
                request.user = viewer
                return widget_class(request=request, user=(self.user if (user is None) else user), viewer=viewer)


        @only_on_speedy_match
        class UserRankWidgetOnlyEnglishTestCase(WidgetTestCaseMixin, SiteTestCase):
            """
            Tests the user rank widget on Speedy Match (English only).

            Methods:
                test_matching_user_can_see_the_rank(self): Asserts a user who matches the profile's user sees the match rank.
                test_user_cannot_see_own_rank(self): Asserts the widget is empty when a user views their own profile.
                test_visitor_cannot_see_the_rank(self): Asserts the widget is empty for a visitor.
                test_blocked_user_cannot_see_the_rank(self): Asserts the widget is empty when there is a block between the viewer and the user.
            """

            def test_matching_user_can_see_the_rank(self):
                """
                Asserts a user who matches the profile's user sees the match rank.
                """
                html = self.get_widget(widget_class=UserRankWidget, viewer=self.viewer).render()
                self.assertIn(member=str(_("Match rank")), container=html)

            def test_user_cannot_see_own_rank(self):
                """
                Asserts the widget is empty when a user views their own profile.
                """
                self.assertEqual(first=self.get_widget(widget_class=UserRankWidget, viewer=self.user).render(), second='')

            def test_visitor_cannot_see_the_rank(self):
                """
                Asserts the widget is empty for a visitor.
                """
                self.assertEqual(first=self.get_widget(widget_class=UserRankWidget, viewer=AnonymousUser()).render(), second='')

            def test_blocked_user_cannot_see_the_rank(self):
                """
                Asserts the widget is empty when there is a block between the viewer and the user.
                """
                Block.objects.block(blocker=self.user, blocked=self.viewer)
                self.assertEqual(first=self.get_widget(widget_class=UserRankWidget, viewer=self.viewer).render(), second='')


        @only_on_speedy_match
        class UserExtraDetailsWidgetOnlyEnglishTestCase(WidgetTestCaseMixin, SiteTestCase):
            """
            Tests the user extra details widget on Speedy Match (English only).

            Methods:
                test_context_data_of_valid_details(self): Asserts the context data contains the user's diet, smoking status and relationship status.
                test_context_data_of_unknown_details(self): Asserts unknown diet, smoking status and relationship status are displayed as "Unknown".
                test_context_data_of_genders_to_match(self): Asserts the genders to match are listed in the context data, or "None" if there are none.
                test_matching_user_can_see_the_details(self): Asserts a user who matches the profile's user sees the extra details.
                test_visitor_cannot_see_the_details(self): Asserts the widget is empty for a visitor.
                test_blocked_user_cannot_see_the_details(self): Asserts the widget is empty when the viewer is blocked by the user.
            """

            def test_context_data_of_valid_details(self):
                """
                Asserts the context data contains the user's diet, smoking status and relationship status.
                """
                cd = self.get_widget(widget_class=UserExtraDetailsWidget, viewer=self.viewer).get_context_data()
                self.assertEqual(first=cd['diet'], second=self.user.get_diet())
                self.assertEqual(first=cd['smoking_status'], second=self.user.get_smoking_status())
                self.assertEqual(first=cd['relationship_status'], second=self.user.get_relationship_status())

            def test_context_data_of_unknown_details(self):
                """
                Asserts unknown diet, smoking status and relationship status are displayed as "Unknown".
                """
                self.user.diet = User.DIET_UNKNOWN
                self.user.smoking_status = User.SMOKING_STATUS_UNKNOWN
                self.user.relationship_status = User.RELATIONSHIP_STATUS_UNKNOWN
                cd = self.get_widget(widget_class=UserExtraDetailsWidget, viewer=self.viewer).get_context_data()
                self.assertEqual(first=cd['diet'], second=str(_("Unknown")))
                self.assertEqual(first=cd['smoking_status'], second=str(_("Unknown")))
                self.assertEqual(first=cd['relationship_status'], second=str(_("Unknown")))

            def test_context_data_of_genders_to_match(self):
                """
                Asserts the genders to match are listed in the context data, or "None" if there are none.
                """
                self.user.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
                cd = self.get_widget(widget_class=UserExtraDetailsWidget, viewer=self.viewer).get_context_data()
                self.assertEqual(first=cd['gender_to_match'], second=str(dict(User.GENDER_CHOICES)[User.GENDER_FEMALE]))
                self.user.speedy_match_profile.gender_to_match = []
                cd = self.get_widget(widget_class=UserExtraDetailsWidget, viewer=self.viewer).get_context_data()
                self.assertEqual(first=cd['gender_to_match'], second=str(_("None")))

            def test_matching_user_can_see_the_details(self):
                """
                Asserts a user who matches the profile's user sees the extra details.
                """
                html = self.get_widget(widget_class=UserExtraDetailsWidget, viewer=self.viewer).render()
                self.assertIn(member=str(_("More Information")), container=html)
                self.assertIn(member=self.user.speedy_match_profile.profile_description, container=html)

            def test_visitor_cannot_see_the_details(self):
                """
                Asserts the widget is empty for a visitor.
                """
                self.assertEqual(first=self.get_widget(widget_class=UserExtraDetailsWidget, viewer=AnonymousUser()).render(), second='')

            def test_blocked_user_cannot_see_the_details(self):
                """
                Asserts the widget is empty when the viewer is blocked by the user.
                """
                Block.objects.block(blocker=self.user, blocked=self.viewer)
                self.assertEqual(first=self.get_widget(widget_class=UserExtraDetailsWidget, viewer=self.viewer).render(), second='')


        @only_on_speedy_match
        class UserOnSpeedyNetWidgetOnlyEnglishTestCase(WidgetTestCaseMixin, SiteTestCase):
            """
            Tests the Speedy Net user widget (defined in speedy.net.profiles) when it is displayed on Speedy Match (English only).

            Methods:
                test_active_user_and_no_block(self): Asserts the context data is positive and the widget is displayed for an active user who is not blocked.
                test_user_viewing_own_profile(self): Asserts the context data is positive when a user views their own profile.
                test_visitor(self): Asserts the context data is negative and the widget is empty for a visitor.
                test_inactive_user_on_speedy_net(self): Asserts the context data is negative when the user is not active on Speedy Net.
                test_blocked_user(self): Asserts the context data is negative and the widget is empty when there is a block between the viewer and the user.
            """

            def test_active_user_and_no_block(self):
                """
                Asserts the context data is positive and the widget is displayed for an active user who is not blocked.
                """
                widget = self.get_widget(widget_class=UserOnSpeedyNetWidget, viewer=self.viewer)
                self.assertIs(expr1=widget.get_context_data()['is_active_and_there_is_no_block'], expr2=True)
                self.assertNotEqual(first=widget.render(), second='')

            def test_user_viewing_own_profile(self):
                """
                Asserts the context data is positive when a user views their own profile.
                """
                widget = self.get_widget(widget_class=UserOnSpeedyNetWidget, viewer=self.user)
                self.assertIs(expr1=widget.get_context_data()['is_active_and_there_is_no_block'], expr2=True)

            def test_visitor(self):
                """
                Asserts the context data is negative and the widget is empty for a visitor.
                """
                widget = self.get_widget(widget_class=UserOnSpeedyNetWidget, viewer=AnonymousUser())
                self.assertIs(expr1=widget.get_context_data()['is_active_and_there_is_no_block'], expr2=False)
                self.assertEqual(first=widget.render(), second='')

            def test_inactive_user_on_speedy_net(self):
                """
                Asserts the context data is negative when the user is not active on Speedy Net.
                """
                user = SpeedyNetInactiveUserFactory()
                widget = self.get_widget(widget_class=UserOnSpeedyNetWidget, viewer=self.viewer, user=user)
                self.assertIs(expr1=widget.get_context_data()['is_active_and_there_is_no_block'], expr2=False)

            def test_blocked_user(self):
                """
                Asserts the context data is negative and the widget is empty when there is a block between the viewer and the user.
                """
                Block.objects.block(blocker=self.user, blocked=self.viewer)
                widget = self.get_widget(widget_class=UserOnSpeedyNetWidget, viewer=self.viewer)
                self.assertIs(expr1=widget.get_context_data()['is_active_and_there_is_no_block'], expr2=False)
                self.assertEqual(first=widget.render(), second='')


