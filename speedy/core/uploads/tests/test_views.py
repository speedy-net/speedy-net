import hashlib
import json
import os
import tempfile

from django.conf import settings as django_settings
from django.core.files.uploadedfile import SimpleUploadedFile

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.uploads.models import File, Image

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    @only_on_sites_with_login
    class UploadViewTestCase(SiteTestCase):
        page_url = '/uploads/upload/'

        def set_up(self):
            super().set_up()
            self.user = ActiveUserFactory()
            self.other_user = ActiveUserFactory()
            upload_file = tempfile.NamedTemporaryFile()
            upload_file.file.write(b'this is a file')
            upload_file.file.seek(0)
            self.data = {
                'file': SimpleUploadedFile(upload_file.name, upload_file.read())
            }
            self.upload_file = upload_file

        def test_visitor_has_no_access(self):
            self.client.logout()
            r = self.client.post(path=self.page_url, data=self.data)
            self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

        def test_upload_file(self):
            initial_images_count = Image.objects.count()
            initial_images_id = list(Image.objects.all().values_list('id', flat=True))
            self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.post(path=self.page_url, data=self.data)
            self.assertEqual(first=r.status_code, second=200)
            json_response = json.loads(r.content.decode())
            self.assertEqual(first=len(json_response['files'][0]['uuid']), second=20)
            self.assertEqual(first=json_response['files'][0]['name'], second=hashlib.md5('$$$-{}-$$$'.format(json_response['files'][0]['uuid']).encode('utf-8')).hexdigest())
            self.assertEqual(first=json_response['files'][0]['type'], second='image')
            self.assertEqual(first=Image.objects.count(), second=initial_images_count + 1)
            image = Image.objects.exclude(id__in=initial_images_id).first()
            assert isinstance(image, Image)
            self.assertEqual(first=str(image.id), second=json_response['files'][0]['uuid'])
            self.assertEqual(first=image.basename, second=json_response['files'][0]['name'])
            self.assertEqual(first=image.size, second=14)
            self.assertEqual(first=image.owner_id, second=self.user.id)

        def test_cannot_delete_files_with_queryset_delete(self):
            with self.assertRaises(NotImplementedError) as cm:
                File.objects.delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                File.objects.all().delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                File.objects.filter(pk=1).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                File.objects.all().exclude(pk=2).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")

        def test_cannot_delete_images_with_queryset_delete(self):
            with self.assertRaises(NotImplementedError) as cm:
                Image.objects.delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                Image.objects.all().delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                Image.objects.filter(pk=1).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                Image.objects.all().exclude(pk=2).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")

