from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class Widget(object):
    template_name = None

    def __init__(self, entity):
        self.entity = entity

    def get_context_data(self):
        return {
            'entity': self.entity,
        }

    def get_template_name(self):
        return self.template_name

    def render(self):
        return mark_safe(render_to_string(self.get_template_name(),
                                self.get_context_data()))

    @property
    def html(self):
        return self.render()


class UserPhotoWidget(Widget):
    template_name = 'profiles/user_photo_widget.html'

class UserInfoWidget(Widget):
    template_name = 'profiles/user_info_widget.html'
