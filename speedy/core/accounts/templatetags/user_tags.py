from django import template

register = template.Library()


@register.inclusion_tag('accounts/profile_picture.html')
def profile_picture(user, geometry, with_link=True, html_class=''):
    return {
        'user': user,
        'geometry': geometry,
        'width': geometry.split('x')[0],
        'with_link': with_link,
        'html_class': html_class,
    }


