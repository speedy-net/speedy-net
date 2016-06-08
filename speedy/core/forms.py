from django import forms


class ModelFormWithDefaults(forms.ModelForm):
    def __init__(self, **kwargs):
        self.defaults = kwargs.pop('defaults', {})
        super().__init__(**kwargs)

    def save(self, commit=True):
        instance = super().save(False)
        for field, value in self.defaults.items():
            setattr(instance, field, value)
        if commit:
            instance.save()
        return instance
