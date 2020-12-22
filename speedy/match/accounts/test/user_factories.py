import random

import factory
import factory.fuzzy

from django.conf import settings as django_settings
from django import test as django_test

from speedy.core.accounts.models import User

if (django_settings.LOGIN_ENABLED):
    _test_case = django_test.TestCase()

    from speedy.core.accounts.test.base_user_factories import DefaultUserFactory
    from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory


    class InactiveUserFactory(DefaultUserFactory):
        pass


    class ActiveUserFactory(DefaultUserFactory):
        @factory.post_generation
        def activate_profile(self, created, extracted, **kwargs):
            from speedy.core.uploads.test.factories import UserImageFactory
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
            self.speedy_match_profile.profile_description = "One two three four five six seven eight nine ten eleven twelve."
            self.city = "Tel Aviv."
            self.speedy_match_profile.children = "One boy."
            self.speedy_match_profile.more_children = "Yes."
            self.speedy_match_profile.match_description = "One two three four five six seven eight."
            self.speedy_match_profile.height = random.randint(150, 220)
            _test_case.assertEqual(first=self.diet, second=User.DIET_UNKNOWN)
            _test_case.assertEqual(first=self.smoking_status, second=User.SMOKING_STATUS_UNKNOWN)
            _test_case.assertEqual(first=self.relationship_status, second=User.RELATIONSHIP_STATUS_UNKNOWN)
            self.diet = random.choice(User.DIET_VALID_VALUES)
            self.smoking_status = random.choice(User.SMOKING_STATUS_VALID_VALUES)
            self.relationship_status = random.choice(User.RELATIONSHIP_STATUS_VALID_VALUES)
            _test_case.assertNotEqual(first=self.diet, second=User.DIET_UNKNOWN)
            _test_case.assertNotEqual(first=self.smoking_status, second=User.SMOKING_STATUS_UNKNOWN)
            _test_case.assertNotEqual(first=self.relationship_status, second=User.RELATIONSHIP_STATUS_UNKNOWN)
            self.speedy_match_profile.gender_to_match = User.GENDER_VALID_VALUES
            self.photo = UserImageFactory(owner=self, visible_on_website=True)
            self.speedy_match_profile.profile_picture_months_offset = 0
            email = UserEmailAddressFactory(user=self, is_confirmed=True)
            email.save()
            email.make_primary()
            self.save_user_and_profile()
            step, error_messages = self.speedy_match_profile.validate_profile_and_activate()
            if (len(error_messages) > 0):
                raise Exception("Error messages not as expected, {}".format(error_messages))
            if (not (step == len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
                raise Exception("Step not as expected, {}".format(step))


