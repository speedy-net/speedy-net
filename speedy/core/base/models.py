from django.core.exceptions import FieldDoesNotExist
from django.db import models

from .managers import BaseManager


class ValidateModelMixin(object):
    """
    Mixin to validate the model before saving.

    Methods:
        save(self, *args, **kwargs): Call `full_clean` before saving the model.
    """
    def save(self, *args, **kwargs):
        """
        Call `full_clean` before saving.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The result of the superclass save method.
        """
        self.full_clean()
        return super().save(*args, **kwargs)


class BaseModel(ValidateModelMixin, models.Model):
    """
    Base model with validation and ID generation.

    Attributes:
        objects (BaseManager): The manager for the model.

    Methods:
        save(self, *args, **kwargs): Save the model, generating an ID if needed.
        generate_id_if_needed(self): Generate an ID if the model does not have one.
    """
    objects = BaseManager()

    def save(self, *args, **kwargs):
        """
        Save the model, generating an ID if needed.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The result of the superclass save method.
        """
        self.generate_id_if_needed()
        kwargs["update_fields"] = None
        return super().save(*args, **kwargs)

    def generate_id_if_needed(self):
        """
        Generate an ID if the model does not have one.

        :raises FieldDoesNotExist: If the 'id' field does not exist.
        """
        try:
            field = self._meta.get_field('id')
            if ((not (self.id)) and (hasattr(field, 'generate_id'))):
                self.id = field.generate_id()
                while (self._meta.model.objects.filter(id=self.id).exists()):
                    self.id = field.generate_id()
        except FieldDoesNotExist:
            pass

    class Meta:
        abstract = True


class TimeStampedModel(BaseModel):
    """
    Abstract base model with timestamp fields.

    Attributes:
        date_created (datetime): The date and time when the model was created.
        date_updated (datetime): The date and time when the model was last updated.
    """
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


