from django.core.exceptions import FieldDoesNotExist
from django.db import models

from .managers import BaseManager


class ValidateModelMixin(object):
    def save(self, *args, **kwargs):
        """
        Call `full_clean` before saving.
        """
        self.full_clean()
        return super().save(*args, **kwargs)


class BaseModel(ValidateModelMixin, models.Model):
    objects = BaseManager()

    def save(self, *args, **kwargs):
        self.generate_id_if_needed()
        kwargs["update_fields"] = None
        return super().save(*args, **kwargs)

    def generate_id_if_needed(self):
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
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


