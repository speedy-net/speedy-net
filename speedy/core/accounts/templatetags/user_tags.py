import copy

from django import template

register = template.Library()


@register.inclusion_tag(filename='accounts/profile_picture.html', takes_context=True)
def profile_picture(context, user, geometry, with_link=True, html_class='', bypass_visible=False):
    context = copy.copy(context)
    geometry_splitted = geometry.split('x')
    width = geometry_splitted[0]
    if (len(geometry_splitted) == 2):
        height = geometry_splitted[1]
    else:
        height = geometry_splitted[0]
    aspect_ratio = round(float(height) / float(width) * 100, 3)
    context.update({
        'user': user,
        'geometry': geometry,
        'width': width,
        'height': height,
        'aspect_ratio': aspect_ratio,
        'with_link': with_link,
        'html_class': html_class,
        'bypass_visible': bypass_visible,
    })
    return context


