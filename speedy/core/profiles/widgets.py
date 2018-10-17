from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class Widget(object):
    template_name = None
    permission_required = 'accounts.view_profile'

    def __init__(self, request, entity, viewer):
        self.request = request
        self.entity = entity
        self.viewer = viewer

    def get_context_data(self):
        return {
            'entity': self.entity,
            'viewer': self.viewer,
        }

    def get_template_name(self):
        return self.template_name

    def get_permission_required(self):
        return self.permission_required

    def render(self):
        if (not (self.viewer.has_perm(perm=self.get_permission_required(), obj=self.entity):
            return ''
        return mark_safe(render_to_string(template_name=self.get_template_name(), context=self.get_context_data(), request=self.request))

    @property
    def html(self):
        return self.render()


class UserPhotoWidget(Widget):
    template_name = 'profiles/user_photo_widget.html'
    permission_required = 'accounts.view_profile_info'


class UserInfoWidget(Widget):
    template_name = 'profiles/user_info_widget.html'
    permission_required = 'accounts.view_profile_info'


