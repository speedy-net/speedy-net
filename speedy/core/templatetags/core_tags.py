from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, url_name):
    return 'active' if context['active_url_name'] == url_name else ''
