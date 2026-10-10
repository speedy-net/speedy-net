from crispy_forms.helper import FormHelper

from django import forms


class ModelFormWithDefaults(forms.ModelForm):
    """
    A ModelForm which applies default field values to the instance when saving, in addition to the submitted form data.

    Attributes:
        defaults (dict): A mapping of field names to default values to apply to the instance on save.

    Methods:
        save: Saves the instance, applying the default field values.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes the form, extracting the `defaults` keyword argument (a mapping of field names to default values).

        :param args: Additional positional arguments, passed to the parent constructor.
        :param kwargs: Additional keyword arguments, passed to the parent constructor. May include `defaults`, a dict of field names to default values.
        """
        self.defaults = kwargs.pop('defaults', {})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Saves the instance, applying the default field values from `self.defaults`.

        :param commit: Whether to save the instance to the database. Default True.
        :type commit: bool
        :return: The saved (or unsaved, if commit is False) instance.
        """
        instance = super().save(commit=False)
        for field, value in self.defaults.items():
            setattr(instance, field, value)
        if (commit):
            instance.save()
        return instance


class FormHelperWithDefaults(FormHelper):
    """
    A crispy-forms FormHelper which renders fields that aren't explicitly mentioned in the layout.

    Attributes:
        render_unmentioned_fields (bool): Whether to render fields that aren't mentioned in the layout. Always True.

    Methods:
        add_default_layout: Adds the form's default layout to the helper.
    """
    render_unmentioned_fields = True

    def add_default_layout(self, form):
        """
        Adds the form's default layout (built by `form.build_default_layout()`) to the helper.

        :param form: The form to build the default layout for.
        """
        self.add_layout(layout=self.build_default_layout(form=form))


class DeleteUnneededFieldsMixin(object):
    """
    A mixin for forms which removes fields that aren't needed.

    Methods:
        delete_unneeded_fields: Deletes unneeded fields from the form.
    """
    def delete_unneeded_fields(self):
        """
        Delete unneeded fields from the form.

        The needed fields are received from `self.get_fields()`.
        """
        fields = self.get_fields()
        fields_for_deletion = set(self.fields.keys()) - set(fields)
        for field_for_deletion in fields_for_deletion:
            del self.fields[field_for_deletion]
        assert (set(self.fields.keys()) == set(fields))


