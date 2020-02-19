import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase

class UserTestCase(TestCase):
    def setUp(self):
        user        = User.objects.create(
                        email       = 'test@test.com',
                        first_name  = 'Mike',
                        username    = 'test@test.com',
                        password    = make_password('test@test')
                        )

    def test_user_created_successfully(self):
        email       = User.objects.get(email='test@test.com')
        self.assertEqual(email.email, 'test@test.com')
