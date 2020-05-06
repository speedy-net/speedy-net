# Define and register Speedy Core path converters.

from django.urls import register_converter


class BaseConverter:
    regex = None

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)


class DigitsConverter(BaseConverter):
    regex = r'[0-9]+'


class SlugConverter(BaseConverter):
    regex = r'[a-zA-Z0-9\-\_\.]+'


register_converter(converter=DigitsConverter, type_name='digits')
register_converter(converter=SlugConverter, type_name='slug')


