from django.core.exceptions import ValidationError


class CleanAndValidateAllFieldsMixin(object):
    def clean_fields(self, exclude=None):
        """
        Allows to have different slug and username validators for Entity and User.
        """
        if exclude is None:
            exclude = []

        self.clean_all_fields(exclude=exclude)

        try:
            super().clean_fields(exclude=exclude)
        except ValidationError as e:
            errors = e.error_dict
        else:
            errors = {}

        self.validate_all_fields(errors=errors, exclude=exclude)

    def clean_all_fields(self, exclude=None):
        pass

    def validate_all_fields(self, errors, exclude=None):
        for field_name, validators in self.validators.items():
            f = self._meta.get_field(field_name)
            if (field_name in exclude):
                pass
            else:
                raw_value = getattr(self, f.attname)
                if ((f.blank) and (raw_value in f.empty_values)):
                    pass
                else:
                    try:
                        for validator in validators:
                            validator(raw_value)
                        if (field_name == 'slug'):
                            self.validate_slug()
                    except ValidationError as e:
                        errors[f.name] = [e.error_list[0].messages[0]]
        if (errors):
            raise ValidationError(errors)

    def validate_slug(self):
        pass


