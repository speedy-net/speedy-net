from speedy.core.base.utils import get_both_genders_context_from_genders
from speedy.core.accounts.models import User


class SpeedyCoreFriendsLanguageMixin(object):
    def _you_already_have_friends_error_message_by_user_number_of_friends_and_gender(self, user_number_of_friends, gender):
        return self._you_already_have_friends_error_message_to_format_dict_by_gender[gender].format(user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

    def _this_user_already_has_friends_error_message_by_other_user_number_of_friends_and_both_genders(self, other_user_number_of_friends, both_genders):
        return self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders[both_genders].format(other_user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

    def set_up(self):
        super().set_up()

        _friendship_request_sent_success_message_dict = {'en': 'Friendship request sent.', 'he': 'בקשת חברות נשלחה.'}
        _friendship_request_accepted_success_message_dict = {'en': 'Friendship request accepted.', 'he': 'בקשת החברות התקבלה.'}
        _friendship_request_rejected_success_message_dict = {'en': 'Friendship request rejected.', 'he': 'בקשת החברות נדחתה.'}
        _youve_cancelled_your_friendship_request_success_message_dict = {'en': "You've cancelled your friendship request.", 'he': 'ביטלת את בקשת החברות שלך.'}

        _you_have_removed_this_user_from_friends_success_message_dict_by_gender = {
            'en': {gender: "You have removed this user from your friends." for gender in User.ALL_GENDERS},
            'he': {
                User.GENDER_FEMALE_STRING: "הסרת את המשתמשת הזאת מהחברים שלך.",
                User.GENDER_MALE_STRING: "הסרת את המשתמש הזה מהחברים שלך.",
                User.GENDER_OTHER_STRING: "הסרת את המשתמש/ת הזאת מהחברים שלך.",
            },
        }

        _you_already_requested_friendship_from_this_user_error_message_dict_by_gender = {
            'en': {gender: "You already requested friendship from this user." for gender in User.ALL_GENDERS},
            'he': {
                User.GENDER_FEMALE_STRING: "כבר ביקשת חברות מהמשתמשת הזאת.",
                User.GENDER_MALE_STRING: "כבר ביקשת חברות מהמשתמש הזה.",
                User.GENDER_OTHER_STRING: "כבר ביקשת חברות מהמשתמש/ת הזאת.",
            },
        }

        _you_already_are_friends_with_this_user_error_message_dict_by_both_genders = {
            'en': {get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "You already are friends with this user." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
            'he': {
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "את כבר חברה של המשתמשת הזאת.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "את כבר חברה של המשתמש הזה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "את כבר חברה של המשתמש/ת הזאת.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "אתה כבר חבר של המשתמשת הזאת.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "אתה כבר חבר של המשתמש הזה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "אתה כבר חבר של המשתמש/ת הזאת.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "את/ה כבר חבר/ה של המשתמשת הזאת.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "את/ה כבר חבר/ה של המשתמש הזה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "את/ה כבר חבר/ה של המשתמש/ת הזאת.",
            },
        }

        _you_cannot_be_friends_with_yourself_error_message_dict_by_gender = {
            'en': {gender: "You cannot be friends with yourself." for gender in User.ALL_GENDERS},
            'he': {
                User.GENDER_FEMALE_STRING: "את לא יכולה להיות חברה של עצמך.",
                User.GENDER_MALE_STRING: "אתה לא יכול להיות חבר של עצמך.",
                User.GENDER_OTHER_STRING: "את/ה לא יכול/ה להיות חבר/ה של עצמך.",
            },
        }

        _you_already_have_friends_error_message_to_format_dict_by_gender = {
            'en': {gender: "You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed." for gender in User.ALL_GENDERS},
            'he': {
                User.GENDER_FEMALE_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסירי חברים/ות לפני שאת ממשיכה.",
                User.GENDER_MALE_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר חברים/ות לפני שאתה ממשיך.",
                User.GENDER_OTHER_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר/י חברים/ות לפני שאת/ה ממשיך/ה.",
            },
        }

        _this_user_already_has_friends_error_message_to_format_dict_by_both_genders = {
            'en': {
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "This user already has {0} friends. She can't have more than {1} friends on Speedy Net. Please ask her to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "This user already has {0} friends. He can't have more than {1} friends on Speedy Net. Please ask him to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "This user already has {0} friends. She can't have more than {1} friends on Speedy Net. Please ask her to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "This user already has {0} friends. He can't have more than {1} friends on Speedy Net. Please ask him to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "This user already has {0} friends. She can't have more than {1} friends on Speedy Net. Please ask her to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "This user already has {0} friends. He can't have more than {1} friends on Speedy Net. Please ask him to remove friends before you proceed.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed.",
            },
            'he': {
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנה להסיר חברים/ות לפני שאת ממשיכה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו להסיר חברים/ות לפני שאת ממשיכה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו/ה להסיר חברים/ות לפני שאת ממשיכה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנה להסיר חברים/ות לפני שאתה ממשיך.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו להסיר חברים/ות לפני שאתה ממשיך.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו/ה להסיר חברים/ות לפני שאתה ממשיך.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנה להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
                get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו/ה להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
            },
        }

        self._friendship_request_sent_success_message = _friendship_request_sent_success_message_dict[self.language_code]
        self._friendship_request_accepted_success_message = _friendship_request_accepted_success_message_dict[self.language_code]
        self._friendship_request_rejected_success_message = _friendship_request_rejected_success_message_dict[self.language_code]
        self._youve_cancelled_your_friendship_request_success_message = _youve_cancelled_your_friendship_request_success_message_dict[self.language_code]

        self._you_have_removed_this_user_from_friends_success_message_dict_by_gender = _you_have_removed_this_user_from_friends_success_message_dict_by_gender[self.language_code]
        self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender = _you_already_requested_friendship_from_this_user_error_message_dict_by_gender[self.language_code]
        self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders = _you_already_are_friends_with_this_user_error_message_dict_by_both_genders[self.language_code]
        self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender = _you_cannot_be_friends_with_yourself_error_message_dict_by_gender[self.language_code]
        self._you_already_have_friends_error_message_to_format_dict_by_gender = _you_already_have_friends_error_message_to_format_dict_by_gender[self.language_code]
        self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders = _this_user_already_has_friends_error_message_to_format_dict_by_both_genders[self.language_code]

        self.assertSetEqual(set1=set(self._you_have_removed_this_user_from_friends_success_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
        self.assertSetEqual(set1=set(self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
        self.assertSetEqual(set1=set(self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders.keys()), set2={get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender) for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS})
        self.assertSetEqual(set1=set(self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
        self.assertSetEqual(set1=set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
        self.assertSetEqual(set1=set(self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders.keys()), set2={get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender) for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS})

        self.assertEqual(first=len(set(self._you_have_removed_this_user_from_friends_success_message_dict_by_gender.keys())), second=3)
        self.assertEqual(first=len(set(self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender.keys())), second=3)
        self.assertEqual(first=len(set(self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders.keys())), second=9)
        self.assertEqual(first=len(set(self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender.keys())), second=3)
        self.assertEqual(first=len(set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys())), second=3)
        self.assertEqual(first=len(set(self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders.keys())), second=9)


