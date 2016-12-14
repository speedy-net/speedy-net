from speedy.core.test import TestCase

from ..middleware import RemoveExtraSlashesMiddleware


class RemoveExtraSlashesMiddlewareTestCase(TestCase):
    def test_normalize_path(self):
        self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/'), second='/zzz/')
        self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/yyy/'), second='/zzz/yyy/')
        self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz/yyy///'), second='/zzz/yyy/')
        self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='////zzz/yyy/'), second='/zzz/yyy/')
        self.assertEqual(first=RemoveExtraSlashesMiddleware.normalize_path(path='/zzz//yyy/'), second='/zzz/yyy/')
