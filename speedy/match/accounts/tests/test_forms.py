from speedy.core.base.test import TestCase, only_on_speedy_match
from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.match.accounts.forms import ProfileNotificationsForm


@only_on_speedy_match
class ProfileNotificationsFormTestCase(TestCase):
    def setup(self):
        self.user = ActiveUserFactory()

    def test_has_correct_fields(self):
        form = ProfileNotificationsForm(instance=self.user)
        self.assertListEqual(list1=list(form.fields.keys()), list2=[
            'notify_on_message',
            'notify_on_like',
        ])


