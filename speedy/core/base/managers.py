from django.contrib.auth import models as django_auth_models
from django.db import models


class QuerySet(models.query.QuerySet):
    def delete(self):
        raise NotImplementedError("delete is not implemented.")


class ManagerMixin(object):
    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError("bulk_create is not implemented.")

    def get_queryset(self):
        """
        Use our own QuerySet model without method .delete().
        """
        return QuerySet(model=self.model, using=self._db, hints=self._hints)


class BaseManager(ManagerMixin, models.Manager):
    pass


class BaseUserManager(ManagerMixin, django_auth_models.BaseUserManager):
    pass


