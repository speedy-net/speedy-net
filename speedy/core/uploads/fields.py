"""
Model and form fields of the Speedy Core uploads app: the file input widget and the photo field (a foreign key to an image).
"""
from typing import TYPE_CHECKING

from django import forms
from django.db import models
from django.template.loader import render_to_string

from .models import File

ImageTypeHintMixin = object
if (TYPE_CHECKING):
    from speedy.core.uploads.models import Image

    ImageTypeHintMixin = Image


class FileInput(forms.TextInput):
    """
    A text input widget for selecting an uploaded file, rendering a preview of the already-uploaded file (if any).
    """

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the widget, including a preview of the file currently referenced by value (if any).

        :param name: The name of the form field.
        :type name: str
        :param value: The primary key of the referenced File instance, if any.
        :type value: str
        :param attrs: Extra HTML attributes for the rendered widget.
        :type attrs: dict or None
        :param renderer: The form renderer to use.
        :type renderer: django.forms.renderers.BaseRenderer or None
        :return: The rendered HTML for the widget.
        :rtype: str
        """
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


class PhotoField(models.ForeignKey, ImageTypeHintMixin):
    """
    A ForeignKey field to an uploaded Image, rendered using FileInput.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the field as a ForeignKey to uploads.Image, setting it to be nulled out on delete and with no reverse relation.

        :param args: Positional arguments passed to ForeignKey.__init__.
        :param kwargs: Keyword arguments passed to ForeignKey.__init__.
        """
        kwargs.update({
            'to': 'uploads.Image',
            'on_delete': models.SET_NULL,
            'related_name': '+',
        })
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Get the form field for this model field, using FileInput as the widget.

        :param kwargs: Keyword arguments passed to the parent formfield method.
        :return: The form field instance.
        :rtype: django.forms.Field
        """
        kwargs.update({
            'widget': FileInput,
        })
        return super().formfield(**kwargs)


