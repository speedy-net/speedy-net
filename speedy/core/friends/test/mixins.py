from speedy.core.accounts.models import User


class SpeedyCoreFriendsLanguageMixin(object):
    def _you_already_have_friends_error_message_by_user_number_of_friends_and_gender(self, user_number_of_friends, gender):
        return self._you_already_have_friends_error_message_to_format_dict_by_gender[gender].format(user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

    def _this_user_already_has_friends_error_message_by_other_user_number_of_friends_and_gender(self, other_user_number_of_friends, gender):
        return self._this_user_already_has_friends_error_message_to_format_dict_by_gender[gender].format(other_user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

    def set_up(self):
        super().set_up()

        _friend_request_sent_success_message_dict = {'en': '+++Friend request sent.', 'he': '___'}
        _friend_request_accepted_success_message_dict = {'en': '+++Friend request accepted.', 'he': '___'}
        _friend_request_rejected_success_message_dict = {'en': '+++Friend request rejected.', 'he': '___'}
        _youve_cancelled_your_friend_request_success_message_dict = {'en': "You've cancelled your friend request.", 'he': '___'}
        _you_have_removed_this_user_from_friends_success_message_dict = {'en': '+++You have removed this user from friends.', 'he': '___'}

        _friendship_already_requested_error_message_dict = {'en': '+++Friendship already requested.', 'he': '___'}
        _users_are_already_friends_error_message_dict = {'en': '+++Users are already friends.', 'he': '___'}
        _users_cannot_be_friends_with_themselves_error_message_dict = {'en': '+++Users cannot be friends with themselves.', 'he': '___'}

        _you_already_have_friends_error_message_to_format_dict_by_gender = {
            'en': {gender: "You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed." for gender in User.ALL_GENDERS},
            'he': {
                User.GENDER_FEMALE_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסירי חברים/ות לפני שאת ממשיכה.",
                User.GENDER_MALE_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר חברים/ות לפני שאתה ממשיך.",
                User.GENDER_OTHER_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר/י חברים/ות לפני שאת/ה ממשיך/ה.",
            },
        }

        # ~~~~ TODO: this translation may depend also on the other user's gender (it depends on both user genders).
        # ~~~~ TODO: maybe this translation to Hebrew is not correct and depends on the wrong gender.
        # ~~~~ TODO: maybe we need different messages in English too, depends on the gender ("them").
        _this_user_already_has_friends_error_message_to_format_dict_by_gender = {
            'en': {gender: "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed." for gender in User.ALL_GENDERS},
            'he': {
                User.GENDER_FEMALE_STRING: "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו/ה להסיר חברים/ות לפני שאת ממשיכה.",
                User.GENDER_MALE_STRING: "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו/ה להסיר חברים/ות לפני שאתה ממשיך.",
                User.GENDER_OTHER_STRING: "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו/ה להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
            },
        }

        self._friend_request_sent_success_message = _friend_request_sent_success_message_dict[self.language_code]
        self._friend_request_accepted_success_message = _friend_request_accepted_success_message_dict[self.language_code]
        self._friend_request_rejected_success_message = _friend_request_rejected_success_message_dict[self.language_code]
        self._youve_cancelled_your_friend_request_success_message = _youve_cancelled_your_friend_request_success_message_dict[self.language_code]
        self._you_have_removed_this_user_from_friends_success_message = _you_have_removed_this_user_from_friends_success_message_dict[self.language_code]

        self._friendship_already_requested_error_message = _friendship_already_requested_error_message_dict[self.language_code]
        self._users_are_already_friends_error_message = _users_are_already_friends_error_message_dict[self.language_code]
        self._users_cannot_be_friends_with_themselves_error_message = _users_cannot_be_friends_with_themselves_error_message_dict[self.language_code]

        self._you_already_have_friends_error_message_to_format_dict_by_gender = _you_already_have_friends_error_message_to_format_dict_by_gender[self.language_code]
        self._this_user_already_has_friends_error_message_to_format_dict_by_gender = _this_user_already_has_friends_error_message_to_format_dict_by_gender[self.language_code]

        self.assertSetEqual(set1=set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
        self.assertSetEqual(set1=set(self._this_user_already_has_friends_error_message_to_format_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))


