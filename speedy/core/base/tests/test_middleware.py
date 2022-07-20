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

        def test_redirect_to_url_without_extra_slashes(self):
            # ~~~~ TODO: fix this test!
            r = self.client.get(path='/about/')
            self.assertEqual(first=r.status_code, second=200)
            r = self.client.get(path='///about/')
            self.assertEqual(first=r.status_code, second=200)  # ~~~~ TODO: should be 301
            # self.assertRedirects(response=r, expected_url='/about/', status_code=301, target_status_code=200)
            r = self.client.get(path='/about///')
            self.assertRedirects(response=r, expected_url='/about/', status_code=301, target_status_code=200)
            r = self.client.get(path='///about///')
            self.assertRedirects(response=r, expected_url='/about/', status_code=301, target_status_code=200)


