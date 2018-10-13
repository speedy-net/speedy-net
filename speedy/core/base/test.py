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


class ErrorsMixin(object):
    # _this_field_is_required_error_message = 'This field is required.'
    _this_field_cannot_be_null_error_message = 'This field cannot be null.'
    _this_field_cannot_be_blank_error_message = 'This field cannot be blank.'
    _id_contains_illegal_characters_error_message = 'id contains illegal characters.'
    _value_must_be_valid_json_error_message = 'Value must be valid JSON.'
    _invalid_password_error_message = 'Invalid password.'
    _password_too_short_error_message = 'Password too short.'
    _password_too_long_error_message = 'Password too long.'
    _you_cant_change_your_username_error_message = "You can't change your username."
    _this_username_is_already_taken_error_message = 'This username is already taken.'
    _enter_a_valid_email_address_error_message = 'Enter a valid email address.'
    _this_email_is_already_in_use_error_message = 'This email is already in use.'
    _enter_a_valid_date_error_message = 'Enter a valid date.'
    _please_enter_a_correct_username_and_password_error_message = 'Please enter a correct username and password. Note that both fields may be case-sensitive.'
    _your_old_password_was_entered_incorrectly_error_message = 'Your old password was entered incorrectly. Please enter it again.'
    _the_two_password_fields_didnt_match_error_message = "The two password fields didn't match."
    _entity_username_must_start_with_4_or_more_letters_error_message = 'Username must start with 4 or more letters, and may contain letters, digits or dashes.'
    _user_username_must_start_with_4_or_more_letters_error_message = 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.'
    _slug_does_not_parse_to_username_error_message = 'Slug does not parse to username.'

    _this_field_is_required_error_message_dict = {'en': 'This field is required.', 'he': 'יש להזין תוכן בשדה זה.'}

    _id_contains_illegal_characters_errors_dict = {'id': [_id_contains_illegal_characters_error_message]}
    _please_enter_a_correct_username_and_password_errors_dict = {'__all__': [_please_enter_a_correct_username_and_password_error_message]}
    _invalid_password_errors_dict = {'password': [_invalid_password_error_message]}
    _password_too_short_errors_dict = {'new_password1': [_password_too_short_error_message]}
    _password_too_long_errors_dict = {'new_password1': [_password_too_long_error_message]}
    _your_old_password_was_entered_incorrectly_errors_dict = {'old_password': [_your_old_password_was_entered_incorrectly_error_message]}
    _the_two_password_fields_didnt_match_errors_dict = {'new_password2': [_the_two_password_fields_didnt_match_error_message]}
    _enter_a_valid_email_address_errors_dict = {'email': [_enter_a_valid_email_address_error_message]}
    _this_email_is_already_in_use_errors_dict = {'email': [_this_email_is_already_in_use_error_message]}
    _enter_a_valid_date_errors_dict = {'date_of_birth': [_enter_a_valid_date_error_message]}
    _you_cant_change_your_username_errors_dict = {'slug': [_you_cant_change_your_username_error_message]}
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
    _cannot_create_user_email_address_without_all_the_required_fields_errors_dict = {'user': [_this_field_cannot_be_null_error_message], 'email': [_this_field_cannot_be_blank_error_message]}

    @staticmethod
    def _value_is_not_a_valid_choice_error_message_by_value(value):
        return 'Value {} is not a valid choice.'.format(value)

    @staticmethod
    def _value_must_be_an_integer_error_message_by_value(value):
        return "'{}' value must be an integer.".format(value)

    @staticmethod
    def _list_contains_items_it_should_contain_no_more_than_3_error_message_by_value(value):
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

    # ~~~~ TODO: simplify these functions! "slug_and_username" etc.

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

    def _registration_form_all_the_required_fields_keys(self):
        return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'last_name_{language_code}', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth']]

    def _registration_form_all_the_required_fields_are_required_errors_dict(self):
        return {field_name: [__class__._this_field_is_required_error_message_dict[self.language_code]] for field_name in self._registration_form_all_the_required_fields_keys()}

    def assert_registration_form_required_fields(self, required_fields):
        self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_are_required_errors_dict().keys()), set2=set(required_fields))
        self.assertDictEqual(d1=self._registration_form_all_the_required_fields_are_required_errors_dict(), d2={field_name: [self._this_field_is_required_error_message_dict[self.language_code]] for field_name in required_fields})


class TestCase(DjangoTestCase):
    def _pre_setup(self):
        super()._pre_setup()
        call_command('loaddata', settings.FIXTURE_DIRS[-1] + '/default_sites_tests.json', verbosity=0)
        self.site = Site.objects.get_current()

    def _validate_all_values(self):
        site_id_dict = {
            settings.SPEEDY_NET_SITE_ID: 1,
            settings.SPEEDY_MATCH_SITE_ID: 2,
            settings.SPEEDY_COMPOSER_SITE_ID: 3,
            settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 5,##TODO
        }
        domain_dict = {
            settings.SPEEDY_NET_SITE_ID: "speedy.net.localhost",
            settings.SPEEDY_MATCH_SITE_ID: "speedy.match.localhost",
            settings.SPEEDY_COMPOSER_SITE_ID: "speedy.composer.localhost",
            settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: "speedy.mail.software.localhost",
        }
        self.assertEqual(first=self.site.id, second=site_id_dict[self.site.id])
        self.assertEqual(first=self.site.domain, second=domain_dict[self.site.id])
        self.assertEqual(first=len(self.all_languages_code_list), second=2)
        self.assertEqual(first=len(self.all_other_languages_code_list), second=1)
        self.assertEqual(first=len(self.all_languages_code_list), second=len(set(self.all_languages_code_list)))
        self.assertEqual(first=len(self.all_other_languages_code_list), second=len(set(self.all_other_languages_code_list)))
        self.assertListEqual(list1=self.all_languages_code_list, list2=['en', 'he'])
        self.assertListEqual(list1=self.all_other_languages_code_list, list2={'en': ['he'], 'he': ['en']}[self.language_code])
        self.assertIn(member=self.language_code, container=self.all_languages_code_list)
        self.assertSetEqual(set1=set(self.all_languages_code_list) - {self.language_code}, set2=set(self.all_other_languages_code_list))
        self.assertEqual(first=self.full_http_host, second='http://{language_code}.{domain}/'.format(language_code=self.language_code, domain=self.site.domain))
        self.assertEqual(first=len(self.all_other_full_http_host_list), second=len(self.all_other_languages_code_list))
        self.assertEqual(first=len(self.all_other_full_http_host_list), second=len(set(self.all_other_full_http_host_list)))
        self.assertListEqual(list1=self.all_other_full_http_host_list, list2={'en': ['http://he.{domain}/'.format(domain=self.site.domain)], 'he': ['http://en.{domain}/'.format(domain=self.site.domain)]}[self.language_code])
        self.validate_language_code()

    def _setup(self):
        self.language_code = settings.LANGUAGE_CODE
        self.all_languages_code_list = [language_code for language_code, language_name in settings.LANGUAGES]
        self.all_other_languages_code_list = [language_code for language_code in self.all_languages_code_list if (not(language_code == self.language_code))]
        self.http_host = "{language_code}.{domain}".format(language_code=self.language_code, domain=self.site.domain)
        self.full_http_host = 'http://{http_host}/'.format(http_host=self.http_host)
        self.all_other_full_http_host_list = ['http://{language_code}.{domain}/'.format(language_code=language_code, domain=self.site.domain) for language_code in self.all_other_languages_code_list]
        self._validate_all_values()
        self.client = self.client_class(HTTP_HOST=self.http_host)
        self.setup()

    def setUp(self):
        super().setUp()
        self._setup()

    def setup(self):
        # No need to call super(), all the setup in this class is done in def _setup.
        pass

    def validate_language_code(self):
        # No need to call super(), all the validation in this class is done in def _validate_all_values.
        pass


exclude_on_site = lambda site_id: conditional_test(test_func=lambda: not(settings.SITE_ID == site_id))
exclude_on_speedy_net = exclude_on_site(site_id=settings.SPEEDY_NET_SITE_ID)
exclude_on_speedy_match = exclude_on_site(site_id=settings.SPEEDY_MATCH_SITE_ID)
exclude_on_speedy_composer = exclude_on_site(site_id=settings.SPEEDY_COMPOSER_SITE_ID)
exclude_on_speedy_mail_software = exclude_on_site(site_id=settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

only_on_site = lambda site_id: conditional_test(test_func=lambda: (settings.SITE_ID == site_id))
only_on_speedy_net = only_on_site(site_id=settings.SPEEDY_NET_SITE_ID)
only_on_speedy_match = only_on_site(site_id=settings.SPEEDY_MATCH_SITE_ID)
only_on_speedy_composer = only_on_site(site_id=settings.SPEEDY_COMPOSER_SITE_ID)
only_on_speedy_mail_software = only_on_site(site_id=settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

only_on_sites = lambda site_id_list: conditional_test(test_func=lambda: (settings.SITE_ID in site_id_list))
only_on_sites_with_login = only_on_sites(site_id_list=[settings.SPEEDY_NET_SITE_ID, settings.SPEEDY_MATCH_SITE_ID])


