from django import forms
from django.db import models
from django.template.loader import render_to_string

from .models import File


class FileInput(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        if (attrs is None):
            attrs = {}
        attrs['data-role'] = 'realInput'
        real_input = super().render(name=name, value=value, attrs=attrs, renderer=renderer)
        files = File.objects.filter(pk=value)
        if (len(files) == 1):
            file = files[0]
        else:
            file = None
        return render_to_string(template_name='uploads/file_input.html', context={
            'real_input': real_input,
            'file': file
        })


class PhotoField(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'to': 'uploads.Image',
            'on_delete': models.SET_NULL,
            'related_name': '+',
        })
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
            'widget': FileInput,
        })
        return super().formfield(**kwargs)


