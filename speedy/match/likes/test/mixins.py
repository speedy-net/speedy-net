from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.accounts.models import User


    class SpeedyMatchLikesLanguageMixin(object):
        def set_up(self):
            super().set_up()

            _list_mutual_title_dict = {'en': "Mutual Likes", 'fr': "J’aimes mutuels", 'de': "Gegenseitige Likes", 'es': "Me gusta mutuos", 'pt': "Curtidas recíproca", 'it': "Mi Piace reciproci", 'nl': "Wederzijdse likes", 'sv': "Ömsesidiga gillanden", 'ko': "상호 좋아요", 'fi': "Yhteiset tykkäämiset", 'he': "לייקים הדדיים"}

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
                    User.GENDER_FEMALE_STRING: "Mädchen, die Sie selbst mögen",
                    User.GENDER_MALE_STRING: "Jungs die Sie selbst mögen",
                    User.GENDER_OTHER_STRING: "Leute, die Sie selbst mögen",
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "Chicas que te gustan",
                    User.GENDER_MALE_STRING: "Chicos que te gustan",
                    User.GENDER_OTHER_STRING: "Gente que te gusta",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "Garotas que tu curtes",
                    User.GENDER_MALE_STRING: "Garotos que tu curtes",
                    User.GENDER_OTHER_STRING: "Pessoas que tu curtes",
                },
                'it': {
                    User.GENDER_FEMALE_STRING: "Le ragazze a cui hai messo Mi Piace",
                    User.GENDER_MALE_STRING: "I ragazzi a cui hai messo Mi Piace",
                    User.GENDER_OTHER_STRING: "Persone a cui hai messo Mi Piace",
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: "Meisjes die je leuk vindt",
                    User.GENDER_MALE_STRING: "Jongens die je leuk vindt",
                    User.GENDER_OTHER_STRING: "Mensen die je leuk vindt",
                },
                'sv': {
                    User.GENDER_FEMALE_STRING: "Tjejer du gillar",
                    User.GENDER_MALE_STRING: "Killar du gillar",
                    User.GENDER_OTHER_STRING: "Folk du gillar",
                },
                'ko': {
                    User.GENDER_FEMALE_STRING: "귀하가 좋아하는 여성",
                    User.GENDER_MALE_STRING: "귀하가 좋아하는 남성",
                    User.GENDER_OTHER_STRING: "귀하가 좋아하는 사람",
                },
                'fi': {
                    User.GENDER_FEMALE_STRING: "Tytöt, joista tykkäät",
                    User.GENDER_MALE_STRING: "Pojat, joista tykkäät",
                    User.GENDER_OTHER_STRING: "Ihmiset, joista tykkäät",
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
                    User.GENDER_FEMALE_STRING: "Mädchen, die Sie mögen",
                    User.GENDER_MALE_STRING: "Jungs, die Sie mögen",
                    User.GENDER_OTHER_STRING: "Leute, die Sie mögen",
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "Chicas a las que les gustas",
                    User.GENDER_MALE_STRING: "Chicos a los que les gustas",
                    User.GENDER_OTHER_STRING: "Gente a la que le gustas",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "Garotas que curtem a ti",
                    User.GENDER_MALE_STRING: "Garotos que curtem a ti",
                    User.GENDER_OTHER_STRING: "Pessoas que curtem a ti",
                },
                'it': {
                    User.GENDER_FEMALE_STRING: "Le ragazze che ti hanno messo Mi Piace",
                    User.GENDER_MALE_STRING: "I ragazzi che ti hanno messo Mi Piace",
                    User.GENDER_OTHER_STRING: "Le persone che ti hanno messo Mi Piace",
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: "Meisjes die je leuk vinden",
                    User.GENDER_MALE_STRING: "Jongens die je leuk vinden",
                    User.GENDER_OTHER_STRING: "Mensen die je leuk vinden",
                },
                'sv': {
                    User.GENDER_FEMALE_STRING: "Tjejer som gillar dig",
                    User.GENDER_MALE_STRING: "Killar som gillar dig",
                    User.GENDER_OTHER_STRING: "Folk som gillar dig",
                },
                'ko': {
                    User.GENDER_FEMALE_STRING: "귀하를 좋아하는 여성",
                    User.GENDER_MALE_STRING: "귀하를 좋아하는 남성",
                    User.GENDER_OTHER_STRING: "귀하를 좋아하는 사람",
                },
                'fi': {
                    User.GENDER_FEMALE_STRING: "Tytöt, jotka tykkäävät sinusta",
                    User.GENDER_MALE_STRING: "Pojat, jotka tykkäävät sinusta",
                    User.GENDER_OTHER_STRING: "Ihmiset, jotka tykkäävät sinusta",
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
                'sv': {
                    **{gender: "Någon gillar dig på Speedy Match" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "누군가가 다음에서 귀하를 좋아합니다 Speedy Match" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Joku tykkää sinusta Speedy Match" for gender in User.ALL_GENDERS},
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


