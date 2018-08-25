from speedy.core.accounts.forms import ModelFormWithDefaults
from .models import File, Image


class FileUploadForm(ModelFormWithDefaults):
    class Meta:
        model = File
        fields = ('file',)


class ImageUploadForm(FileUploadForm):
    class Meta(FileUploadForm.Meta):
        model = Image


