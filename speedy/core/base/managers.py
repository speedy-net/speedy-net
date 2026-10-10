"""
Base model managers and querysets of Speedy Core.
"""
from django.contrib.auth import models as django_auth_models
from django.db import models


class QuerySet(models.query.QuerySet):
    """
    A QuerySet which disables bulk deletion.

    Methods:
        delete: Always raises NotImplementedError.
    """
    def delete(self):
        """
        Disables bulk deletion of querysets.

        :raises NotImplementedError: Always, since bulk deletion is not allowed.
        """
        raise NotImplementedError("delete is not implemented.")


class ManagerMixin(object):
    """
    A mixin for managers which disables bulk creation and bulk deletion, and returns our own QuerySet (without method .delete()).

    Methods:
        bulk_create: Always raises NotImplementedError.
        delete: Always raises NotImplementedError.
        get_queryset: Returns our own QuerySet without method .delete().
    """
    def bulk_create(self, *args, **kwargs):
        """
        Disables bulk creation of objects.

        :param args: Positional arguments (ignored).
        :param kwargs: Keyword arguments (ignored).
        :raises NotImplementedError: Always, since bulk creation is not allowed.
        """
        raise NotImplementedError("bulk_create is not implemented.")

    def delete(self):
        """
        Disables bulk deletion of objects.

        :raises NotImplementedError: Always, since bulk deletion is not allowed.
        """
        raise NotImplementedError("delete is not implemented.")

    def get_queryset(self):
        """
        Use our own QuerySet model without method .delete().

        :return: A QuerySet instance without a working .delete() method.
        :rtype: QuerySet
        """
        return QuerySet(model=self.model, using=self._db, hints=self._hints)


class BaseManager(ManagerMixin, models.Manager):
    """
    The base manager for Speedy Core models, which disables bulk creation and bulk deletion.
    """
    pass


class BaseUserManager(ManagerMixin, django_auth_models.BaseUserManager):
    """
    The base manager for Speedy Core user models, which disables bulk creation and bulk deletion.
    """
    pass


