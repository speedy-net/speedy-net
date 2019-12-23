import json
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, *url_names):
    return 'active' if (context['active_url_name'] in url_names) else ''


@register.simple_tag(takes_context=True)
def set_request_params(context, **params):
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
    sliced_page_range is [1, None, 4, 5, 6, 7, 8, None, 42]
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
    if (value == "en"):
        return "www"
    else:
        return value


@register.filter
def jsonify(object):
    return json.dumps(object)


@register.filter
def key_value(dictionary, key):
    return dictionary.get(str(key))


