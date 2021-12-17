from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net
        from speedy.core.accounts.tests.test_forms import ProfileNotificationsFormTestCaseMixin
        from speedy.core.accounts.forms import ProfileNotificationsForm


        @only_on_speedy_net
        class ProfileNotificationsFormTestCase(ProfileNotificationsFormTestCaseMixin, SiteTestCase):
            def test_has_correct_fields(self):
                form = ProfileNotificationsForm(instance=self.user)
                self.assertListEqual(list1=list(form.fields.keys()), list2=[
                    'notify_on_message',
                ])


