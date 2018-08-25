import json

import os
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from ..models import Image


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class UploadViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        upload_file = tempfile.NamedTemporaryFile()
        upload_file.file.write(b'this is a file')
        upload_file.file.seek(0)
        self.data = {
            'file': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        self.upload_file = upload_file
        self.page_url = '/uploads/upload/'

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_upload_file(self):
        initial_images_count = Image.objects.count()
        initial_images_id = list(Image.objects.all().values_list('id', flat=True))
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(first=r.status_code, second=200)
        json_response = json.loads(r.content.decode())
        self.assertEqual(first=len(json_response['files'][0]['uuid']), second=20)
        self.assertEqual(first=json_response['files'][0]['name'], second=os.path.basename(self.upload_file.name))
        self.assertEqual(first=json_response['files'][0]['type'], second='image')
        self.assertEqual(first=Image.objects.count(), second=initial_images_count + 1)
        image = Image.objects.exclude(id__in=initial_images_id).first()
        assert isinstance(image, Image)
        self.assertEqual(first=str(image.id), second=json_response['files'][0]['uuid'])
        self.assertEqual(first=image.basename, second=json_response['files'][0]['name'])
        self.assertEqual(first=image.size, second=14)
        self.assertEqual(first=image.owner_id, second=self.user.id)


