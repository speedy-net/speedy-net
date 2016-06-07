from django.test import TestCase

from .models import Entity, User


class RegistrationViewTestCase(TestCase):

    def setUp(self):
        self.valid_data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'email@example.com',
            'gender': 1,
            'password1': 'password',
            'password2': 'password',
        }

    def test_visitor_can_see_registration_page(self):
        r = self.client.get('/register/')
        self.assertEqual(200, r.status_code)
        self.assertTemplateUsed(r, 'accounts/registration.html')

    def test_visitor_can_register(self):
        r = self.client.post('/register/', data=self.valid_data)
        self.assertRedirects(r, '/register/success/')
        self.assertEqual(1, Entity.objects.count())
        self.assertEqual(1, User.objects.count())
        entity = Entity.objects.all()[0]
        user = User.objects.all()[0]
        self.assertEqual(user, entity.user)
        self.assertEqual(user.id, entity.id)
        self.assertEqual(15, len(entity.id))
        self.assertTrue(user.check_password('password'))
        self.assertEqual('First', user.first_name)
        self.assertEqual('First', user.first_name_en)
        self.assertEqual('Last', user.last_name)
        self.assertEqual('Last', user.last_name_en)
        self.assertEqual('email@example.com', user.email)
