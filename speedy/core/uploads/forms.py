from speedy.core.base.forms import ModelFormWithDefaults
from .models import File, Image


class FileUploadForm(ModelFormWithDefaults):
    """
    Form for uploading a File.
    """
    class Meta:
        model = File
        fields = ('file',)


class ImageUploadForm(FileUploadForm):
    """
    Form for uploading an Image.
    """
    class Meta(FileUploadForm.Meta):
        model = Image


