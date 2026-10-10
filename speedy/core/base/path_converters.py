# Define and register Speedy Core path converters.

from django.urls import register_converter


class BaseConverter:
    """
    A base class for Speedy Core URL path converters.

    Attributes:
        regex (str): The regular expression used to match this converter's value in the URL. Must be set by subclasses.

    Methods:
        to_python: Converts the matched string from the URL to a Python value.
        to_url: Converts a Python value to a string for use in a URL.
    """
    regex = None

    def to_python(self, value):
        """
        Converts the matched string from the URL to a Python value.

        :param value: The matched string from the URL.
        :type value: str
        :return: The value, converted to str.
        :rtype: str
        """
        return str(value)

    def to_url(self, value):
        """
        Converts a Python value to a string for use in a URL.

        :param value: The value to convert.
        :return: The value, converted to str.
        :rtype: str
        """
        return str(value)


class DigitsConverter(BaseConverter):
    """
    A path converter which matches one or more digits.
    """
    regex = r'[0-9]+'


class SpeedySlugConverter(BaseConverter):
    """
    A path converter which matches a Speedy slug (letters, digits, hyphens, underscores and dots).
    """
    regex = r'[a-zA-Z0-9\-\_\.]+'


register_converter(converter=DigitsConverter, type_name='digits')
register_converter(converter=SpeedySlugConverter, type_name='speedy_slug')


