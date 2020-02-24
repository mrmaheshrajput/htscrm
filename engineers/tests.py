import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from engineers.models import Engineer
from engineers.forms import EngineerAddForm
from engineers.views import EngineerEditView

class EngineerFormTest(TestCase):

    def test_EngineerForm_valid(self):
        form            = EngineerAddForm(
            data={
                'engineer_name': 'Lo Lo',
                'mobile': '9898887888'
            }
        )
        self.assertTrue(form.is_valid())

    def test_EngineerForm_invalid_mobile(self):
        form            = EngineerAddForm(
            data={
                'engineer_name': 'Lo Lo',
                'mobile': '98988878'
            }
        )
        self.assertFalse(form.is_valid())

    def test_EngineerForm_blank_mobile(self):
        form            = EngineerAddForm(
            data={
                'engineer_name': 'Lo Lo',
                'mobile': ''
            }
        )
        self.assertFalse(form.is_valid())


class EngineerTestCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user        = User.objects.create(
                        email           = 'test@test.com',
                        first_name      = 'Mike',
                        username        = 'test@test.com',
                        password        = make_password('test@test  ')
                        )
        cls.engineer    = Engineer.objects.create(
                        added_by        = cls.user,
                        engineer_name   = 'GoGo Go',
                        mobile          = '989878678'
                        )

    def setUp(self):
        self.user.refresh_from_db()
        self.engineer.refresh_from_db()


    def test_engineer_page_without_login(self):
        r           = self.client.get(reverse('engineers:engineer_view'))
        self.assertEqual(r.status_code, 302)


    def test_engineer_create(self):
        self.assertEqual(self.engineer.engineer_name, 'GoGo Go')
        self.assertEqual(self.engineer.added_by, self.user)


    def test_engineer_page_after_login(self):
        user_login = self.client.login(username=self.user.email, password='test@test  ')
        self.assertTrue(user_login)
        response = self.client.get(reverse('engineers:engineer_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.engineer.engineer_name)
        self.assertContains(response, self.engineer.mobile)


    def test_engineer_edit_view_valid_details(self):
        self.client.force_login(self.user)
        data     = {
            'engineer_name': 'Jawla Pasand',
            'mobile':'9888778889',
            'eng-id':self.engineer.id
            }
        response = self.client.post(reverse('engineers:engineer_edit_view'), data)
        self.assertEqual(response.status_code, 302)

        page     = self.client.get(reverse('engineers:engineer_view'))
        self.assertEqual(page.status_code, 200)

        self.assertNotIn(b'GoGo Go', page.content)
        self.assertIn(b'Jawla', page.content)
        self.client.logout()


    def test_engineer_edit_view_invalid_details(self):
        self.client.force_login(self.user)
        data     = {
            'engineer_name': 'Jawla Pasand',
            'eng-id':self.engineer.id
            }
        response = self.client.post(reverse('engineers:engineer_edit_view'), data)
        self.assertEqual(response.status_code, 302)

        page     = self.client.get(reverse('engineers:engineer_view'))
        self.assertEqual(page.status_code, 200)

        self.assertNotIn(b'Jawla', page.content)
        self.assertIn(b'GoGo Go', page.content)
        self.client.logout()


    def test_engineer_delete_view_valid_id(self):
        self.client.force_login(self.user)
        data   = {'engineer-id':self.engineer.id}
        response = self.client.post(reverse('engineers:engineer_delete_view'),
            data=data)
        page    = self.client.get(reverse('engineers:engineer_view'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(page.status_code, 200)
        self.assertNotIn(b'GoGo Go', page.content)
        self.assertNotIn(b'Jawla Pasand', page.content)


    def test_engineer_delete_view_invalid_id(self):
        self.client.force_login(self.user)
        data   = {'engineer-id':self.engineer.id + 1}
        response = self.client.post(reverse('engineers:engineer_delete_view'),
            data=data)
        self.assertEqual(response.status_code, 302)

        page    = self.client.get(reverse('engineers:engineer_view'))
        self.assertEqual(page.status_code, 200)

        self.assertIn(b'Failed', page.content)
