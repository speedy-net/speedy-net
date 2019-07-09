from crispy_forms.helper import FormHelper
from django import forms


class ModelFormWithDefaults(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.defaults = kwargs.pop('defaults', {})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field, value in self.defaults.items():
            setattr(instance, field, value)
        if (commit):
            instance.save()
        return instance


class FormHelperWithDefaults(FormHelper):
    render_unmentioned_fields = True


class DeleteUnneededFieldsMixin(object):
    def delete_unneeded_fields(self):
        fields = self.get_fields()
        fields_for_deletion = set(self.fields.keys()) - set(fields)
        for field_for_deletion in fields_for_deletion:
            del self.fields[field_for_deletion]


