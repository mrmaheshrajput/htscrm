import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class LoginPageAuthenticatonTestCases(TestCase):
    # def setUp(self):
    #     self.user        = User.objects.create(
    #                     email       = 'test@test.com',
    #                     first_name  = 'Mike',
    #                     username    = 'test@test.com',
    #                     password    = make_password('test@test  ')
    #                     )

    @classmethod
    def setUpTestData(cls):
        cls.user        = User.objects.create(
                        email       = 'test@test.com',
                        first_name  = 'Mike',
                        username    = 'test@test.com',
                        password    = make_password('test@test  ')
                        )

    def test_login_page(self):
        r           = self.client.get(reverse('accounts:login'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/signin.html')

    def test_setup_user_creation(self):
        self.assertEqual(self.user.email, 'test@test.com')
        self.assertIs(check_password('test@test  ', self.user.password), True)

    def test_login_without_password(self):
        r           = authenticate(username=self.user.email, password=None)
        self.assertEqual(r, None)

    def test_login_without_email(self):
        r           = authenticate(username=None, password='test@test  ')
        self.assertEqual(r, None)

    def test_login_without_email_password(self):
        r           = authenticate(username=None, password=None)
        self.assertEqual(r, None)

    def test_login_sqlinjection_in_password(self):
        r           = authenticate(
                        username=self.user.email,
                        password="'1' or '1 = 1"
                        )
        self.assertEqual(r, None)

    def test_login_authentication(self):
        response    = authenticate(username=self.user.email, password='test@test  ')
        self.assertEqual(
            response.email, self.user.email
        )


class RegisterPageTestCases(TestCase):

    def test_register_page(self):
        r           = self.client.get(reverse('accounts:register'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'accounts/register.html')

    def test_register_valid_details(self):
        user        = User.objects.create(
                        email       = 'test@test.com',
                        first_name  = 'Mike',
                        username    = 'test@test.com',
                        password    = make_password('test@test  ')
        )
        self.assertEqual(user.email, 'test@test.com')
