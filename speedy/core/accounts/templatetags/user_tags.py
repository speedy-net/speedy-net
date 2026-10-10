"""
Template tags of the Speedy Core accounts app, containing the profile picture inclusion tag.
"""
import copy

from django import template

register = template.Library()


@register.inclusion_tag(filename='accounts/profile_picture.html', takes_context=True)
def profile_picture(context, user, geometry, with_link=True, html_class='', bypass_visible=False):
    """
    Build the template context for rendering a user's profile picture inclusion tag.

    :param context: The current template context.
    :type context: django.template.Context
    :param user: The user whose profile picture is being rendered.
    :type user: speedy.core.accounts.models.User
    :param geometry: The geometry string for the picture, e.g. "100x100" or "100".
    :type geometry: str
    :param with_link: Whether the picture should be wrapped in a link to the user's profile.
    :type with_link: bool
    :param html_class: Extra CSS class(es) to add to the picture element.
    :type html_class: str
    :param bypass_visible: Whether to bypass the profile picture visibility check.
    :type bypass_visible: bool
    :return: The updated template context for the inclusion tag.
    :rtype: django.template.Context
    """
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


