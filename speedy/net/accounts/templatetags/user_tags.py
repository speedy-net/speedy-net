from django import template

register = template.Library()


@register.inclusion_tag('accounts/profile_picture.html')
def profile_picture(user, geometry, with_link=True):
    return {
        'user': user,
        'geometry': geometry,
        'with_link': with_link,
    }
