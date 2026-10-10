"""
Test cases which check the PostgreSQL database configuration of Speedy Core.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from django.db import connection

    from speedy.core.base.test.models import SiteTestCase


    class PostgresqlOnlyEnglishTestCase(SiteTestCase):
        """
        Tests the PostgreSQL server version used by the database connection, in English.
        """
        def test_postgresql_version(self):
            """
            Tests that the connected PostgreSQL server's version is at least 14.0.
            """
            postgresql_version = connection.cursor().connection.info.server_version
            if (postgresql_version >= 140000):
                pass
            else:
                raise NotImplementedError("postgresql version must be at least 14.0.")


