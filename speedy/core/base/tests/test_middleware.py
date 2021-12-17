from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.middleware import RemoveExtraSlashesMiddleware


    class RemoveExtraSlashesMiddlewareTestCase(SiteTestCase):
        def test_normalize_path(self):
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/'), second='/zzz/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/yyy/'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/yyy///'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='////zzz/yyy/'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz//yyy/'), second='/zzz/yyy/')
            self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='////xxx////yyy////'), second='/xxx/yyy/')


