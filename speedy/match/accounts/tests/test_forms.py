from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match
from speedy.match.accounts.forms import ProfileNotificationsForm

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


@only_on_speedy_match
class ProfileNotificationsFormTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user = ActiveUserFactory()

    def test_has_correct_fields(self):
        form = ProfileNotificationsForm(instance=self.user)
        self.assertListEqual(list1=list(form.fields.keys()), list2=[
            'notify_on_message',
            'notify_on_like',
        ])


