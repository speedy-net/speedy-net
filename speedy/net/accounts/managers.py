from django.contrib.auth.models import BaseUserManager
from django.db.models import Q


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(Q(**{self.model.USERNAME_FIELD: username}) |
                        Q(email_addresses__email=username))
