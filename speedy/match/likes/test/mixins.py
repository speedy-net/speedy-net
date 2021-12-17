from django.conf import settings as django_settings

from speedy.core.accounts.models import User


if (django_settings.TESTS):
    class SpeedyMatchLikesLanguageMixin(object):
        def set_up(self):
            super().set_up()

            _list_mutual_title_dict = {'en': "Mutual Likes", 'he': "לייקים הדדיים"}

            _list_to_title_dict_by_gender = {
                'en': {
                    User.GENDER_FEMALE_STRING: "Girls You Like",
                    User.GENDER_MALE_STRING: "Boys You Like",
                    User.GENDER_OTHER_STRING: "People You Like",
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "בנות שעשית להן לייק",
                    User.GENDER_MALE_STRING: "בנים שעשית להם לייק",
                    User.GENDER_OTHER_STRING: "אנשים שעשית להם לייק",
                },
            }
            _list_from_title_dict_by_gender = {
                'en': {
                    User.GENDER_FEMALE_STRING: "Girls Who Like You",
                    User.GENDER_MALE_STRING: "Boys Who Like You",
                    User.GENDER_OTHER_STRING: "People Who Like You",
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "בנות שעשו לך לייק",
                    User.GENDER_MALE_STRING: "בנים שעשו לך לייק",
                    User.GENDER_OTHER_STRING: "אנשים שעשו לך לייק",
                },
            }
            _someone_likes_you_on_speedy_match_subject_dict_by_gender = {
                'en': {
                    **{gender: "Someone likes you on Speedy Match" for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "מישהי עשתה לך לייק בספידי מץ'",
                    User.GENDER_MALE_STRING: "מישהו עשה לך לייק בספידי מץ'",
                    User.GENDER_OTHER_STRING: "מישהו עשה לך לייק בספידי מץ'",
                },
            }

            self._list_mutual_title = _list_mutual_title_dict[self.language_code]

            self._list_to_title_dict_by_gender = _list_to_title_dict_by_gender[self.language_code]
            self._list_from_title_dict_by_gender = _list_from_title_dict_by_gender[self.language_code]
            self._someone_likes_you_on_speedy_match_subject_dict_by_gender = _someone_likes_you_on_speedy_match_subject_dict_by_gender[self.language_code]

            self.assertSetEqual(set1=set(self._list_to_title_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._list_from_title_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._someone_likes_you_on_speedy_match_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))

            self.assertEqual(first=len(set(self._list_to_title_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._list_from_title_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._someone_likes_you_on_speedy_match_subject_dict_by_gender.keys())), second=3)


