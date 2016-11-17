import json
import os
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from speedy.core.test import TestCase

from speedy.net.accounts.tests.test_factories import UserFactory
from ..models import Image


class UploadViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
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
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_upload_file(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(r.status_code, 200)
        json_response = json.loads(r.content.decode())
        self.assertEqual(len(json_response['files'][0]['uuid']), 15)
        self.assertEqual(json_response['files'][0]['name'], os.path.basename(self.upload_file.name))
        self.assertEqual(json_response['files'][0]['type'], 'image')
        self.assertEqual(Image.objects.count(), 1)
        image = Image.objects.first()
        assert isinstance(image, Image)
        self.assertEqual(str(image.id), json_response['files'][0]['uuid'])
        self.assertEqual(image.basename, json_response['files'][0]['name'])
        self.assertEqual(image.size, 14)
        self.assertEqual(image.owner_id, self.user.id)
