import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from customers.models import ClientDetails
from customers.forms import ClientForm

class CustomerFormTest(TestCase):

    def test_ClientForm_valid(self):
        form            = ClientForm(
            data={
                'name': 'Lo Lo',
                'calling_number': '9898887888',
                'contact_number': '9878778909'
            }
        )
        self.assertTrue(form.is_valid())

    def test_ClientForm_invalid_number(self):
        form            = ClientForm(
            data={
                'name': 'Lo Lo',
                'calling_number': '9898887888',
                'contact_number': '987877899'
            }
        )
        self.assertFalse(form.is_valid())

    def test_ClientForm_missing_number(self):
        form            = ClientForm(
            data={
                'name': 'Lo Lo',
                'calling_number': '9898887888'
            }
        )
        self.assertFalse(form.is_valid())


class CustomerTestCases(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user        = User.objects.create(
                        email           = 'test@test.com',
                        first_name      = 'Mike',
                        username        = 'test@test.com',
                        password        = make_password('test@test  ')
                        )
        cls.customer    = ClientDetails.objects.create(
                        created_by      = cls.user,
                        name            = 'GoGo Go',
                        calling_number  = '989878678',
                        contact_number  = '989878678'
                        )

    def setUp(self):
        self.user.refresh_from_db()
        self.customer.refresh_from_db()


    def test_customer_page_without_login(self):
        r           = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(r.status_code, 302)


    def test_customer_create(self):
        self.assertEqual(self.customer.name, 'GoGo Go')
        self.assertEqual(self.customer.created_by, self.user)


    def test_customer_page_after_login(self):
        user_login = self.client.login(username=self.user.email, password='test@test  ')
        self.assertTrue(user_login)
        response = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.customer.name)
        self.assertContains(response, self.customer.contact_number)


    def test_customer_create_view_valid_details(self):
        self.client.force_login(self.user)
        data = {
            'name': 'Umrao Jaan',
            'calling_number': '8789889878',
            'contact_number':'1234567890',
            'next': ''
        }
        request = self.client.post(reverse('customers:customer_create_view'), data)
        self.assertEqual(request.status_code, 302)

        response = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(response.status_code, 200)

        print(response.content)
        self.assertIn(b'Success', response.content)
        self.assertIn(b'Umrao', response.content)


    def test_customer_create_view_invalid_number(self):
        self.client.force_login(self.user)
        data = {
            'name': 'Umrao Jaan',
            'calling_number': '8789889878',
            'contact_number':'1234567891122',
            'next': ''
        }
        request = self.client.post(reverse('customers:customer_create_view'), data)
        self.assertEqual(request.status_code, 302)

        response = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'Failed', response.content)
        self.assertNotIn(b'Umrao', response.content)


    def test_customer_create_view_missing_number(self):
        self.client.force_login(self.user)
        data = {
            'name': 'Umrao Jaan',
            'calling_number': '8789889878',
            'next': ''
        }
        request = self.client.post(reverse('customers:customer_create_view'), data)
        self.assertEqual(request.status_code, 302)

        response = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(response.status_code, 200)

        self.assertIn(b'Failed', response.content)
        self.assertNotIn(b'Umrao', response.content)


    def test_customer_detail_view_post_request(self):
        self.client.force_login(self.user)
        request = self.client.post(reverse('customers:customer_detail_view'),
                    {'id':self.customer.id})
        self.assertEqual(request.status_code, 200)
        self.assertIn(self.customer.name, request.content.decode('utf8'))


    def test_customer_list_api(self):
        request = self.client.get(reverse('customers:customer_list_api'))
        self.assertEqual(request.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse('customers:customer_list_api'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.customer.name, response.content.decode('utf8'))


    def test_customer_delete_view_valid_id(self):
        self.client.force_login(self.user)
        data   = {'customer-id':self.customer.id}
        request = self.client.post(reverse('customers:customer_delete_view'),
            data=data)
        self.assertEqual(request.status_code, 302)

        response    = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.content)
        self.assertNotIn(b'GoGo Go', response.content)


    def test_customer_delete_view_invalid_id(self):
        self.client.force_login(self.user)
        data   = {'customer-id':self.customer.id + 1}
        request = self.client.post(reverse('customers:customer_delete_view'),
            data=data)
        self.assertEqual(request.status_code, 302)

        response    = self.client.get(reverse('customers:customer_detail_view'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Failed', response.content)
        self.assertIn(b'GoGo Go', response.content)


    def test_customer_edit_view_get_request_valid_id(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('customers:customer_edit_view', kwargs={'id':self.customer.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GoGo Go', response.content)


    # def test_customer_edit_view_get_request_invalid_id(self):
    #     self.client.force_login(self.user)
    #     response = self.client.get(reverse('customers:customer_edit_view', kwargs={'id':self.customer.id + 1}))
    #     self.assertEqual(response.status_code, 302)
    #     self.assertIn(b'Failed', response.content)


    # def test_customer_edit_view_post_request_valid(self):
    #     self.client.force_login(self.user)
    #     data = {
    #         'name': 'Begum Jaan',
    #         'contact_number': '989878678',
    #         'calling_number': '9898887888',
    #         'address': '1234, Main Street',
    #         'pin': '122002'
    #     }
    #     request = self.client.post(reverse('customers:customer_edit_view',
    #                                 kwargs={'id':self.customer.id}),
    #                     data=data)
    #     self.assertEqual(request.status_code, 302)
    #
    #     response    = self.client.get(reverse('customers:customer_detail_view'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotIn(b'GoGo Go', response.content)
    #     self.assertIn(b'Begum', response.content)
