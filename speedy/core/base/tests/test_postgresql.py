from django.conf import settings as django_settings

if (django_settings.TESTS):
    from django.db import connection

    from speedy.core.base.test.models import SiteTestCase


    class PostgresqlOnlyEnglishTestCase(SiteTestCase):
        def test_postgresql_version(self):
            postgresql_version = connection.cursor().connection.server_version
            if (postgresql_version >= 140000):
                pass
            else:
                raise NotImplementedError("postgresql version must be at least 14.0.")


