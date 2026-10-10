"""
Profile widgets of Speedy Core: a base widget class that renders a template, and the user photo and user info widgets displayed on user profile pages.
"""
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class Widget(object):
    """
    Base class for profile widgets, rendering a template for a user's profile if the viewer has the required permission.

    Attributes:
        template_name (str): The name of the template to render.
        permission_required (str): The permission required to view the widget.

    Methods:
        html(self): Property returning the rendered HTML of the widget.
        get_context_data(self): Get the context data for rendering the widget's template.
        get_template_name(self): Get the name of the template to render.
        get_permission_required(self): Get the permission required to view the widget.
        render(self): Render the widget's template, or an empty string if the viewer lacks permission.
    """
    template_name = None
    permission_required = 'accounts.view_profile'

    @property
    def html(self):
        """
        Get the rendered HTML of the widget.

        :return: The rendered HTML, or an empty string if the viewer lacks permission.
        :rtype: str
        """
        return self.render()

    def __init__(self, request, user, viewer):
        """
        Initialize the widget.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param user: The user whose profile the widget belongs to.
        :type user: speedy.core.accounts.models.User
        :param viewer: The entity viewing the profile.
        :type viewer: speedy.core.accounts.models.Entity
        """
        self.request = request
        self.user = user
        self.viewer = viewer

    def get_context_data(self):
        """
        Get the context data for rendering the widget's template.

        :return: A dict with the user and viewer.
        :rtype: dict
        """
        return {
            'user': self.user,
            'viewer': self.viewer,
        }

    def get_template_name(self):
        """
        Get the name of the template to render.

        :return: The template name.
        :rtype: str
        """
        return self.template_name

    def get_permission_required(self):
        """
        Get the permission required to view the widget.

        :return: The required permission.
        :rtype: str
        """
        return self.permission_required

    def render(self):
        """
        Render the widget's template if the viewer has the required permission.

        :return: The rendered HTML, or an empty string if the viewer lacks permission.
        :rtype: str
        """
        if (not (self.viewer.has_perm(perm=self.get_permission_required(), obj=self.user))):
            return ''
        return mark_safe(s=render_to_string(template_name=self.get_template_name(), context=self.get_context_data(), request=self.request))


class UserPhotoWidget(Widget):
    """
    Widget that renders a user's profile photo.
    """
    template_name = 'profiles/user_photo_widget.html'
    permission_required = 'accounts.view_profile_info'


class UserInfoWidget(Widget):
    """
    Widget that renders a user's profile info.
    """
    template_name = 'profiles/user_info_widget.html'
    permission_required = 'accounts.view_profile_info'


