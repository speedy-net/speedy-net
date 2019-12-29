import copy

from django import template

register = template.Library()


@register.inclusion_tag(filename='accounts/profile_picture.html', takes_context=True)
def profile_picture(context, user, geometry, with_link=True, html_class=''):
    context = copy.copy(context)
    context.update({
        'user': user,
        'geometry': geometry,
        'width': geometry.split('x')[0],
        'with_link': with_link,
        'html_class': html_class,
    })
    return context


