import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from calls.models import CallRegister, CallAllocation
from calls.forms import CallRegisterForm
from customers.models import ClientDetails
from engineers.models import Engineer


class CallRegisterFormTest(TestCase):

    def test_CallRegisterForm_valid(self):
        form            = CallRegisterForm(
            data={
                'complaint_nature': 'Wet Service',
                'appointment_date': datetime.date.today()
            }
        )
        self.assertTrue(form.is_valid())

    def test_CallRegisterForm_invalid(self):
        form            = CallRegisterForm(
            data={
                'complaint_nature': ''
            }
        )
        self.assertFalse(form.is_valid())

    def test_CallRegisterForm_all_fields(self):
        form            = CallRegisterForm(
            data={
                'complaint_nature': 'Service',
                'brand': 'PLC',
                'product_name': 'JCW',
                'product_serial': '678SDD233DS',
                'product_coverage': True,
                'appointment_date': datetime.date.today(),
                'appointment_time': datetime.datetime.now().strftime('%H:%M:%S')
            }
        )
        self.assertTrue(form.is_valid())


class CallViewTestCases(TestCase):
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
        cls.call        = CallRegister.objects.create(
                        customer        = cls.customer,
                        complaint_nature= 'Wet Service Required',
                        brand           = 'PLC',
                        product_name    = 'JCW',
                        product_serial  = '678SDD233DS',
                        product_coverage= True,
                        appointment_date= datetime.date.today(),
                        appointment_time= datetime.datetime.now().strftime('%H:%M:%S')
        )
        cls.engineer    = Engineer.objects.create(
                        added_by        = cls.user,
                        engineer_name   = 'Ramakant Dubey',
                        mobile          = '1234567890'
        )

    # def setUp(self):
    #     self.user.refresh_from_db()
    #     self.customer.refresh_from_db()

    def test_call_page_without_login(self):
        response = self.client.get(reverse('calls:calls_list_view'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.content)


    def test_call_page_with_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:calls_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calls/calls_list_view.html')
        self.assertIn(b'Wet Service', response.content)


    def test_call_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:calls_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calls/calls_list_view.html')
        self.assertIn(b'GoGo Go', response.content)
        self.assertIn(b'Wet Service', response.content)
        self.assertIn(b'Allocate Now', response.content)


    def test_call_detail_view_without_allocation_visit(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_detail_view',
                        kwargs={'id':self.call.id}))
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calls/call_detail_view.html')
        self.assertIn(b'GoGo Go', response.content)
        self.assertIn(b'989878678', response.content)
        self.assertIn(b'Wet Service Required', response.content)
        self.assertIn(b'PLC', response.content)
        self.assertIn(b'JCW', response.content)
        self.assertIn(b'678SDD233DS', response.content)
        # self.assertContains(response, datetime.date.today().strftime('%B %d, %Y'))
        # self.assertContains(response, datetime.date.today().strftime('%I:%M'))
        self.assertIn(b'Unallocated call', response.content)


    def test_call_complain_api(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_complain_api'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.call.complaint_nature)


    def test_call_register_view(self):
        self.client.force_login(self.user)
        request = self.client.get(reverse('calls:call_register_view'))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request, 'calls/call_create_view.html')

        data = {
            'customer-id': self.customer.pk,
            'complaint_nature': 'Dry Pumping Service',
            'appointment_date': datetime.date.today()
        }
        response = self.client.post(reverse('calls:call_register_view'),
                                    data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.content)
        self.assertIn(b'Dry Pumping', response.content)


    def test_call_register_view_invalid_customer(self):
        self.client.force_login(self.user)
        request = self.client.get(reverse('calls:call_register_view'))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request, 'calls/call_create_view.html')

        data = {
            'customer-id': self.customer.pk + 1,
            'complaint_nature': 'Dry Pumping Service',
            'appointment_date': datetime.date.today()
        }
        response = self.client.post(reverse('calls:call_register_view'),
                                    data, follow=True)
        self.assertEqual(response.status_code, 404)


    def test_call_register_view_invalid_details(self):
        self.client.force_login(self.user)
        request = self.client.get(reverse('calls:call_register_view'))
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request, 'calls/call_create_view.html')

        data = {
            'customer-id': self.customer.pk
        }
        response = self.client.post(reverse('calls:call_register_view'),
                                    data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Failed', response.content)


    def test_call_allocation_view(self):
        self.client.force_login(self.user)
        data = {
            'call-id': self.call.id,
            'engineer-id':self.engineer.id,
            'next':''
        }
        response = self.client.post(reverse('calls:call_allocate_view'),
                                            data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.content)
        self.assertContains(response, self.engineer.engineer_name)


    def test_call_allocation_view_invalid_call(self):
        self.client.force_login(self.user)
        data = {
            'call-id': self.call.id + 1,
            'engineer-id':self.engineer.id,
            'next':''
        }
        response = self.client.post(reverse('calls:call_allocate_view'),
                                            data, follow=True)
        self.assertEqual(response.status_code, 404)


    def test_call_allocation_view_invalid_engineer(self):
        self.client.force_login(self.user)
        data = {
            'call-id': self.call.id,
            'engineer-id':self.engineer.id + 1,
            'next':''
        }
        response = self.client.post(reverse('calls:call_allocate_view'),
                                            data, follow=True)
        self.assertEqual(response.status_code, 404)


    def test_call_edit_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_edit_view',
                                kwargs={'id':self.call.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'calls/call_edit_view.html')


    def test_call_edit_view_get_invalid_call(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_edit_view',
                                kwargs={'id':self.call.id+1}))
        self.assertEqual(response.status_code,404)


    def test_call_edit_view_post_request(self):
        self.client.force_login(self.user)
        customer_two = ClientDetails.objects.create(
                        created_by      = self.user,
                        name            = 'Jane Doe',
                        calling_number  = '1111222233',
                        contact_number  = '4444555566'
                        )
        data = {
            'customer-id'       : customer_two.id,
            'complaint_nature'  : 'Gas Recharge',
            'brand'             : 'PLC',
            'product_name'      : 'JCW',
            'product_serial'    : '678SDD233DS',
            'product_coverage'  : True,
            'appointment_date'  : datetime.date.today(),
            'appointment_time'  : datetime.datetime.now().strftime('%H:%M:%S')
        }
        response = self.client.post(reverse('calls:call_edit_view',
                kwargs={'id':self.call.id}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.content)
        self.assertIn(b'Jane Doe', response.content)
        self.assertIn(b'Gas', response.content)
        self.assertNotIn(b'GoGo Go', response.content)


    def test_call_edit_view_post_invalid_customer(self):
        self.client.force_login(self.user)
        data = {
            'customer-id'       : self.customer.id + 1,
            'complaint_nature'  : 'Gas Recharge',
            'brand'             : 'PLC',
            'product_name'      : 'JCW',
            'product_serial'    : '678SDD233DS',
            'product_coverage'  : True,
            'appointment_date'  : datetime.date.today(),
            'appointment_time'  : datetime.datetime.now().strftime('%H:%M:%S')
        }
        response = self.client.post(reverse('calls:call_edit_view',
                kwargs={'id':self.call.id}), data, follow=True)
        self.assertEqual(response.status_code, 404)


    def test_call_edit_view_post_invalid_call(self):
        self.client.force_login(self.user)
        data = {
            'customer-id'       : self.customer.id,
            'complaint_nature'  : 'Gas Recharge',
            'brand'             : 'PLC',
            'product_name'      : 'JCW',
            'product_serial'    : '678SDD233DS',
            'product_coverage'  : True,
            'appointment_date'  : datetime.date.today(),
            'appointment_time'  : datetime.datetime.now().strftime('%H:%M:%S')
        }
        response = self.client.post(reverse('calls:call_edit_view',
                kwargs={'id':self.call.id + 1}), data, follow=True)
        self.assertEqual(response.status_code, 404)


    def test_call_edit_view_post_incomplete_details(self):
        self.client.force_login(self.user)
        data = {
            'customer-id'       : self.customer.id,
            'complaint_nature'  : ''
        }
        response = self.client.post(reverse('calls:call_edit_view',
                kwargs={'id':self.call.id}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Failed', response.content)
        self.assertIn(b'GoGo Go', response.content)
        self.assertIn(b'Wet Service', response.content)
        self.assertNotIn(b'Jane Doe', response.content)
        self.assertNotIn(b'Gas', response.content)


    def test_call_detail_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_detail_view',
                                kwargs={'id':self.call.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'calls/call_detail_view.html')
        self.assertIn(b'Wet Service', response.content)
        self.assertIn(b'GoGo Go', response.content)
        self.assertIn(b'989878678', response.content)
        self.assertIn(b'Unallocated call', response.content)


    def test_call_detail_view_invalid_call(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_detail_view',
                                kwargs={'id':self.call.id+1}))
        self.assertEqual(response.status_code,404)


    def test_call_detail_view_allocated(self):
        self.client.force_login(self.user)
        data = {
            'call-id': self.call.id,
            'engineer-id':self.engineer.id,
            'next':''
        }
        request = self.client.post(reverse('calls:call_allocate_view'),
                                            data, follow=True)
        self.assertEqual(request.status_code,200)
        self.assertIn(b'Success', request.content)

        response = self.client.get(reverse('calls:call_detail_view',
                                kwargs={'id':self.call.id}))
        self.assertEqual(response.status_code,200)
        self.assertIn(b'Ramakant Dubey', response.content)
        self.assertIn(b'Pending', response.content)
        self.assertNotIn(b'Expired', response.content)


    def test_call_detail_view_allocated_twice(self):
        self.client.force_login(self.user)
        data = {
            'call-id': self.call.id,
            'engineer-id':self.engineer.id,
            'next':''
        }
        request = self.client.post(reverse('calls:call_allocate_view'),
                                            data, follow=True)
        self.assertEqual(request.status_code,200)
        self.assertIn(b'Success', request.content)

        data_new = {
            'call-id': self.call.id,
            'engineer-id':self.engineer.id,
            'next':''
        }
        request_two = self.client.post(reverse('calls:call_allocate_view'),
                                            data_new, follow=True)
        self.assertEqual(request_two.status_code,200)
        self.assertIn(b'Success', request_two.content)

        response = self.client.get(reverse('calls:call_detail_view',
                                kwargs={'id':self.call.id}))
        self.assertEqual(response.status_code,200)
        self.assertIn(b'Ramakant Dubey', response.content)
        self.assertIn(b'Expired', response.content)
        self.assertIn(b'Pending', response.content)


    def test_call_detail_view_visit(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('calls:call_detail_view',
                                kwargs={'id':self.call.id}))
        self.assertEqual(response.status_code,200)
        self.assertNotIn(b'Visit History', response.content)
