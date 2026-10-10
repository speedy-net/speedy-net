"""
Template tags and filters of Speedy Core, such as active_class, set_request_params, pagination and filters which convert domain names between the www, en and he sites.
"""
import json

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, *url_names):
    """
    Returns the CSS class "active" if the current active URL name is one of the given URL names.

    :param context: Required. The template context.
    :param url_names: Required. One or more URL names to check against the active URL name.
    :return: "active" if the current active URL name is one of `url_names`, otherwise an empty string.
    :rtype: str
    """
    return 'active' if (context['active_url_name'] in url_names) else ''


@register.simple_tag(takes_context=True)
def set_request_params(context, **params):
    """
    Builds a query string from the current request's GET parameters, updated with the given params, dropping the "page" parameter if it is 1.

    :param context: Required. The template context, containing the current request.
    :param params: Required. Query string parameters to set (or override) on the request's GET parameters.
    :return: A query string (starting with "?"), or an empty string if there are no parameters and no request.
    :rtype: str
    """
    request = context.get('request')
    if (request):
        query_dict = request.GET.copy()
        for k, v in params.items():
            query_dict[k] = v
        if ("page" in query_dict):
            if (str(query_dict["page"]) == str(1)):
                del query_dict["page"]
        if (query_dict.urlencode() == ""):
            return ""
        else:
            return "?{}".format(query_dict.urlencode())


@register.inclusion_tag(filename='core/pagination.html', takes_context=True)
def pagination(context):
    """
    Builds a sliced range of page numbers to show in the pagination widget, with gaps (represented by None) collapsing distant pages.

    sliced_page_range is [1, None, 4, 5, 6, 7, 8, None, 42]

    :param context: Required. The template context, containing the current paginator and page_obj.
    :return: The context, updated with a 'sliced_page_range' key.
    :rtype: dict
    """
    full_page_range = list(context['paginator'].page_range)
    page_index = context['page_obj'].number - 1
    sliced_page_range = full_page_range[max(page_index - 2, 0):page_index + 3]

    if (full_page_range[0] != sliced_page_range[0]):
        if (full_page_range[1] != sliced_page_range[0]):
            sliced_page_range.insert(0, None)
        sliced_page_range.insert(0, full_page_range[0])

    if (full_page_range[-1] != sliced_page_range[-1]):
        if (full_page_range[-2] != sliced_page_range[-1]):
            sliced_page_range.append(None)
        sliced_page_range.append(full_page_range[-1])

    context['sliced_page_range'] = sliced_page_range
    return context


@register.filter
def convert_en_to_www(value):
    """
    Converts the language code "en" to "www", leaving other values unchanged.

    :param value: Required. The value to convert.
    :return: "www" if `value` is "en", otherwise `value` unchanged.
    """
    if (value == "en"):
        return "www"
    else:
        return value


@register.filter
def convert_non_he_to_www(value):
    """
    Converts any value other than "he" to "www", leaving "he" unchanged.

    :param value: Required. The value to convert.
    :return: "www" if `value` is not "he", otherwise "he".
    """
    if (not (value == "he")):
        return "www"
    else:
        return value


@register.filter
def convert_non_he_to_en(value):
    """
    Converts any value other than "en" or "he" to "en", leaving "en" and "he" unchanged.

    :param value: Required. The value to convert.
    :return: "en" if `value` is neither "en" nor "he", otherwise `value` unchanged.
    """
    if (not (value in {"en", "he"})):
        return "en"
    else:
        return value


@register.filter
def jsonify(object):
    """
    Serializes a value to a JSON string.

    :param object: Required. The value to serialize.
    :return: A JSON string representing the value.
    :rtype: str
    """
    return json.dumps(object)


@register.filter
def key_value(dictionary, key):
    """
    Looks up a key (converted to a string) in a dictionary.

    :param dictionary: Required. The dictionary to look up the key in.
    :type dictionary: dict
    :param key: Required. The key to look up (will be converted to a string).
    :return: The value for the key, or None if not found.
    """
    return dictionary.get(str(key))


