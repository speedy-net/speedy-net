import inspect

from django.conf import settings
from django.core.management import call_command
from django.contrib.sites.models import Site
from django.test import TestCase as DjangoTestCase
from django.test.runner import DiscoverRunner

from speedy.core.settings.utils import env


class SiteDiscoverRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = [label for label in settings.INSTALLED_APPS if label.startswith('speedy.')]
        return super().build_suite(test_labels=test_labels, extra_tests=extra_tests, **kwargs)


class SpeedyCoreDiscoverRunner(SiteDiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # We don't run tests on speedy.core
        pass


def conditional_test(test_func):
    def wrapper(method_or_class):
        if inspect.isclass(method_or_class):
            # Decorate class
            if test_func():
                return method_or_class
            else:
                return
        else:
            # Decorate method
            def inner(*args, **kwargs):
                if test_func():
                    return method_or_class(*args, **kwargs)
                else:
                    return

            return inner

    return wrapper


class TestCase(DjangoTestCase):
    client_host = 'en.localhost'

    _this_field_is_required_error_message = 'This field is required.'
    _this_field_cannot_be_null_error_message = '___This field cannot be null.'
    _this_field_cannot_be_blank_error_message = '___This field cannot be blank.'
    _id_contains_illegal_characters_error_message = '___id contains illegal characters'
    _value_must_be_valid_json_error_message = '___Value must be valid JSON.'
    _invalid_password_error_message = 'Invalid password.'
    _password_too_short_error_message = '___Password too short.'
    _password_too_long_error_message = '___Password too long.'
    _this_username_is_already_taken_error_message = 'This username is already taken.'
    _this_email_is_already_in_use_error_message = 'This email is already in use.'
    _please_enter_a_correct_username_and_password_error_message = '___Please enter a correct username and password. Note that both fields may be case-sensitive.'
    _your_old_password_was_entered_incorrectly_error_message = '___Your old password was entered incorrectly. Please enter it again.'
    _the_two_password_fields_didnt_match_error_message = "___The two password fields didn't match."
    _entity_username_must_start_with_4_or_more_letters_error_message = '___Username must start with 4 or more letters, and may contain letters, digits or dashes.'
    _user_username_must_start_with_4_or_more_letters_error_message = 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'
    _slug_does_not_parse_to_username_error_message = '___Slug does not parse to username.'

    _id_contains_illegal_characters_errors_dict = {'id': [_id_contains_illegal_characters_error_message]}
    _please_enter_a_correct_username_and_password_errors_dict = {'__all__': [_please_enter_a_correct_username_and_password_error_message]}
    _invalid_password_errors_dict = {'password': [_invalid_password_error_message]}
    _password_too_short_errors_dict = {'new_password1': [_password_too_short_error_message]}
    _password_too_long_errors_dict = {'new_password1': [_password_too_long_error_message]}
    _your_old_password_was_entered_incorrectly_errors_dict = {'old_password': [_your_old_password_was_entered_incorrectly_error_message]}
    _the_two_password_fields_didnt_match_errors_dict = {'new_password2': [_the_two_password_fields_didnt_match_error_message]}
    _this_email_is_already_in_use_errors_dict = {'email': [_this_email_is_already_in_use_error_message]}
    _slug_this_username_is_already_taken_errors_dict = {'slug': [_this_username_is_already_taken_error_message]}
    _slug_and_username_this_username_is_already_taken_errors_dict = {'username': [_this_username_is_already_taken_error_message], 'slug': [_this_username_is_already_taken_error_message]}
    _entity_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict = {'username': [_entity_username_must_start_with_4_or_more_letters_error_message], 'slug': [_entity_username_must_start_with_4_or_more_letters_error_message]}
    _entity_username_username_must_start_with_4_or_more_letters_errors_dict = {'username': [_entity_username_must_start_with_4_or_more_letters_error_message]}
    _entity_slug_username_must_start_with_4_or_more_letters_errors_dict = {'slug': [_entity_username_must_start_with_4_or_more_letters_error_message]}
    _user_slug_and_username_username_must_start_with_4_or_more_letters_errors_dict = {'username': [_user_username_must_start_with_4_or_more_letters_error_message], 'slug': [_user_username_must_start_with_4_or_more_letters_error_message]}
    _user_username_username_must_start_with_4_or_more_letters_errors_dict = {'username': [_user_username_must_start_with_4_or_more_letters_error_message]}
    _user_slug_username_must_start_with_4_or_more_letters_errors_dict = {'slug': [_user_username_must_start_with_4_or_more_letters_error_message]}
    _slug_does_not_parse_to_username_errors_dict = {'slug': [_slug_does_not_parse_to_username_error_message]}
    _entity_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict = {'username': [_entity_username_must_start_with_4_or_more_letters_error_message], 'slug': [_slug_does_not_parse_to_username_error_message]}
    _user_username_must_start_with_4_or_more_letters_and_slug_does_not_parse_to_username_errors_dict = {'username': [_user_username_must_start_with_4_or_more_letters_error_message], 'slug': [_slug_does_not_parse_to_username_error_message]}
    _registration_form_all_the_required_fields_are_required_errors_dict = {'first_name_en': [_this_field_is_required_error_message], 'last_name_en': [_this_field_is_required_error_message], 'email': [_this_field_is_required_error_message], 'slug': [_this_field_is_required_error_message], 'new_password1': [_this_field_is_required_error_message], 'gender': [_this_field_is_required_error_message], 'date_of_birth': [_this_field_is_required_error_message]}

    @staticmethod
    def _value_is_not_a_valid_choice_error_message_by_value(value):
        return '___Value {} is not a valid choice.'.format(value)
        return 'Value {} is not a valid choice.'.format(value)

    @staticmethod
    def _value_must_be_an_integer_error_message_by_value(value):
        return "___'{}' value must be an integer.".format(value)
        return "'{}' value must be an integer.".format(value)

    @staticmethod
    def _list_contains_items_it_should_contain_no_more_than_3_error_message_by_value(value):
        return '___List contains {} items, it should contain no more than 3.'.format(len(value))
        return 'List contains {} items, it should contain no more than 3.'.format(len(value))

    @staticmethod
    def _ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length, value_length):
        return 'Ensure this value has at least {} characters (it has {}).'.format(min_length, value_length)

    @staticmethod
    def _ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length, value_length):
        return 'Ensure this value has at most {} characters (it has {}).'.format(max_length, value_length)

    @staticmethod
    def _this_field_cannot_be_null_errors_dict_by_field_name(field_name):
        return {field_name: [__class__._this_field_cannot_be_null_error_message]}

    @staticmethod
    def _this_field_cannot_be_blank_errors_dict_by_field_name(field_name):
        return {field_name: [__class__._this_field_cannot_be_blank_error_message]}

    @staticmethod
    def _value_must_be_valid_json_errors_dict_by_field_name(field_name):
        return {field_name: [__class__._value_must_be_valid_json_error_message]}

    @staticmethod
    def _value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(field_name, value):
        return {field_name: [__class__._value_is_not_a_valid_choice_error_message_by_value(value=value)]}

    @staticmethod
    def _value_must_be_an_integer_errors_dict_by_field_name_and_value(field_name, value):
        return {field_name: [__class__._value_must_be_an_integer_error_message_by_value(value=value)]}

    @staticmethod
    def _list_contains_items_it_should_contain_no_more_than_3_errors_dict_by_field_name_and_value(field_name, value):
        return {field_name: [__class__._list_contains_items_it_should_contain_no_more_than_3_error_message_by_value(value=value)]}

    @staticmethod
    def _this_field_cannot_be_null_errors_dict_by_field_name_list(field_name_list):
        return {field_name_list[i]: [__class__._this_field_cannot_be_null_error_message] for i in range(len(field_name_list))}

    @staticmethod
    def _value_must_be_an_integer_errors_dict_by_field_name_list_and_value_list(field_name_list, value_list):
        return {field_name_list[i]: [__class__._value_must_be_an_integer_error_message_by_value(value=value_list[i])] for i in range(len(field_name_list))}

    @staticmethod
    def _entity_slug_and_username_min_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)], 'slug': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    @staticmethod
    def _user_slug_and_username_min_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)], 'slug': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    @staticmethod
    def _entity_username_min_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    @staticmethod
    def _user_username_min_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    @staticmethod
    def _entity_slug_min_length_fail_errors_dict_by_value_length(value_length):
        return {'slug': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    @staticmethod
    def _user_slug_min_length_fail_errors_dict_by_value_length(value_length):
        return {'slug': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=value_length)]}

    @staticmethod
    def _entity_slug_and_username_max_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=120, value_length=value_length)], 'slug': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    @staticmethod
    def _user_slug_and_username_max_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=40, value_length=value_length)], 'slug': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    @staticmethod
    def _entity_username_max_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=120, value_length=value_length)]}

    @staticmethod
    def _user_username_max_length_fail_errors_dict_by_value_length(value_length):
        return {'username': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=40, value_length=value_length)]}

    @staticmethod
    def _entity_slug_max_length_fail_errors_dict_by_value_length(value_length):
        return {'slug': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    @staticmethod
    def _user_slug_max_length_fail_errors_dict_by_value_length(value_length):
        return {'slug': [__class__._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=200, value_length=value_length)]}

    @staticmethod
    def _cannot_create_user_without_all_the_required_fields_errors_dict():
        return {'first_name': [__class__._this_field_cannot_be_blank_error_message], 'last_name': [__class__._this_field_cannot_be_blank_error_message], 'username': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=0)], 'slug': [__class__._ensure_this_value_has_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=6, value_length=0)], 'password': [__class__._this_field_cannot_be_blank_error_message], 'gender': [__class__._this_field_cannot_be_null_error_message], 'date_of_birth': [__class__._this_field_cannot_be_null_error_message]}

    def setUp(self):
        super().setUp()
        self.set_up()

    def set_up(self):
        pass

    def _pre_setup(self):
        super()._pre_setup()
        call_command('loaddata', settings.FIXTURE_DIRS[-1] + '/default_sites_local.json', verbosity=0)
        self.site = Site.objects.get_current()
        self.site.domain = 'localhost'
        self.site.save()
        self.SPEEDY_NET_SITE_ID = settings.SITE_PROFILES.get('net').get('site_id')
        self.SPEEDY_MATCH_SITE_ID = settings.SITE_PROFILES.get('match').get('site_id')
        self.client = self.client_class(HTTP_HOST=self.client_host)


exclude_on_site = lambda site_id: conditional_test(lambda: int(settings.SITE_ID) != int(site_id))
exclude_on_speedy_net = exclude_on_site(env('SPEEDY_NET_SITE_ID'))
exclude_on_speedy_match = exclude_on_site(env('SPEEDY_MATCH_SITE_ID'))
exclude_on_speedy_composer = exclude_on_site(env('SPEEDY_COMPOSER_SITE_ID'))
exclude_on_speedy_mail_software = exclude_on_site(env('SPEEDY_MAIL_SOFTWARE_SITE_ID'))

only_on_site = lambda site_id: conditional_test(lambda: int(settings.SITE_ID) == int(site_id))
only_on_speedy_net = only_on_site(env('SPEEDY_NET_SITE_ID'))
only_on_speedy_match = only_on_site(env('SPEEDY_MATCH_SITE_ID'))
only_on_speedy_composer = only_on_site(env('SPEEDY_COMPOSER_SITE_ID'))
only_on_speedy_mail_software = only_on_site(env('SPEEDY_MAIL_SOFTWARE_SITE_ID'))


