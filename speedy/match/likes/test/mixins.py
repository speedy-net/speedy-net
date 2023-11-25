from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.accounts.models import User


    class SpeedyMatchLikesLanguageMixin(object):
        def set_up(self):
            super().set_up()

            _list_mutual_title_dict = {'en': "Mutual Likes", 'fr': "J’aimes mutuels", 'de': "_____ # ~~~~ TODO", 'es': "_____ # ~~~~ TODO", 'pt': "_____ # ~~~~ TODO", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'he': "לייקים הדדיים"}

            _list_to_title_dict_by_gender = {
                'en': {
                    User.GENDER_FEMALE_STRING: "Girls You Like",
                    User.GENDER_MALE_STRING: "Boys You Like",
                    User.GENDER_OTHER_STRING: "People You Like",
                },
                'fr': {
                    User.GENDER_FEMALE_STRING: "Les filles que vous aimez",
                    User.GENDER_MALE_STRING: "Les garçons que vous aimez",
                    User.GENDER_OTHER_STRING: "Les personnes que vous aimez",
                },
                'de': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'it': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
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
                'fr': {
                    User.GENDER_FEMALE_STRING: "Les filles qui vous aiment",
                    User.GENDER_MALE_STRING: "Les garçons qui vous aiment",
                    User.GENDER_OTHER_STRING: "Les personnes qui vous aiment",
                },
                'de': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'it': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_MALE_STRING: "_____ # ~~~~ TODO",
                    User.GENDER_OTHER_STRING: "_____ # ~~~~ TODO",
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
                'fr': {
                    **{gender: "Quelqu’un vous aime bien sur Speedy Match" for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Jemand likt Sie am Speedy Match" for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: "Le gustas a alguien Speedy Match" for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "Alguém curte a ti no Speedy Match" for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "Qualcuno ti ha messo Mi Piace su Speedy Match" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: "Iemand vindt je leuk op Speedy Match",
                    User.GENDER_MALE_STRING: "Iemand vindt je leuk op Speedy Match",
                    User.GENDER_OTHER_STRING: "Iemand vindt jullie leuk op Speedy Match",
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


