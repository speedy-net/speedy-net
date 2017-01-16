from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()


@register.inclusion_tag('accounts_core/profile_picture.html')
def profile_picture(user, geometry, with_link=True, html_class=''):
    return {
        'user': user,
        'geometry': geometry,
        'width': geometry.split('x')[0],
        'with_link': with_link,
        'html_class': html_class,
    }
