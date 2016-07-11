from django import forms
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string

from .models import File

class FileInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['data-role'] = 'realInput'
        real_input = super().render(name, value, attrs)
        try:
            file = File.objects.get(id=value)
        except File.DoesNotExist:
            file = None
        return render_to_string('uploads/file_input.html', {
            'real_input': real_input,
            'file': file
        })


class PhotoField(models.ForeignKey):
    def __init__(self, **kwargs):
        kwargs.update({
            'to': 'uploads.Image',
            'on_delete': models.SET_NULL,
            'related_name': '+',
        })
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
            'widget': FileInput,
        })
        return super().formfield(**kwargs)
