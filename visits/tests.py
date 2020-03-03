import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from calls.models import CallRegister, CallAllocation
from customers.models import ClientDetails
from engineers.models import Engineer
from visits.forms import CallVisitForm
from visits.models import CallVisit


class CallVisitFormTestCases(TestCase):
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
                        engineer_name   = 'Ramakant Dubey',
                        mobile          = '1234567890'
        )


    def test_CallVisitForm_valid(self):
        form = CallVisitForm(
            data = {
                'serviced_by': self.engineer,
                'visit_status': 'CNA',
                'visit_date_time': datetime.datetime.now(),
                'outcome': 'Nice',
                'call_status_final': True,
                'call_visit_final_notes': 'None'
            }
        )
        self.assertTrue(form.is_valid())


    def test_CallVisitForm_invalid_engineer(self):
        form = CallVisitForm(
            data = {
                'serviced_by': self.engineer.id + 1,
                'visit_status': 'CNA',
                'visit_date_time': datetime.datetime.now(),
                'outcome': 'Nice',
                'call_status_final': True,
                'call_visit_final_notes': 'None'
            }
        )
        self.assertFalse(form.is_valid())


    def test_CallVisitForm_invalid_details(self):
        form = CallVisitForm(
            data = {
                'serviced_by': self.engineer.id,
                'visit_status': 'CNA'
            }
        )
        self.assertFalse(form.is_valid())


class CallVisitTestCases(TestCase):
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
        cls.engineer    = Engineer.objects.create(
                        added_by        = cls.user,
                        engineer_name   = 'Ramakant Dubey',
                        mobile          = '1234567890'
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
        cls.allocation  = CallAllocation.objects.create(
                        call                  = cls.call,
                        engineer_assigned     = cls.engineer
        )
        cls.visit       = CallVisit.objects.create(
                        callallocation_id       = cls.allocation,
                        call_id                 = cls.call,
                        serviced_by             = cls.engineer,
                        visit_status            = 'CVD',
                        visit_date_time         = datetime.datetime.now(),
                        outcome                 = 'Lorem ipsum dolor sit amet, consectetur',
                        call_status_final       = True,
                        call_visit_final_notes  = 'Revisit required'
        )

    # def setUp(self):
    #     self.client.force_login(self.user)


    def test_visit_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('visits:visit_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visits/visit_list_view.html')
        self.assertIn(b'Revisit', response.content)


    def test_visit_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('visits:visit_create_view',
                                    kwargs={'id':self.call.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visits/visit_create_view.html')


    def test_visit_create_view_get_invalid(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('visits:visit_create_view',
                                    kwargs={'id':self.call.id + 1}))
        self.assertEqual(response.status_code, 404)


    def test_visit_create_view_get_unallocated_call(self):
        call        = CallRegister.objects.create(
                        customer        = self.customer,
                        complaint_nature= 'Gas Recharge',
                        brand           = 'JCB',
                        product_name    = 'Roller',
                        product_serial  = 'RZA43A2A286-194',
                        product_coverage= False,
                        appointment_date= datetime.date.today(),
                        appointment_time= datetime.datetime.now().strftime('%H:%M:%S')
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('visits:visit_create_view',
                                    kwargs={'id':call.id}))
        self.assertEqual(response.status_code, 404)


    def test_visit_create_view_post(self):
        self.client.force_login(self.user)
        data = {
            'serviced_by': self.engineer.id,
            'visit_status': 'CNA',
            'visit_date_time': datetime.datetime.now(),
            'outcome': 'Nice',
            'call_status': 'Open',
            'call_status_final': False,
            'call_visit_final_notes': 'Ok Report'
        }
        response = self.client.post(reverse('visits:visit_create_view',
                    kwargs={'id':self.allocation.id}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.content)
        self.assertIn(b'Ok Report', response.content)


    def test_visit_create_view_post_invalid_details(self):
        self.client.force_login(self.user)
        data = {
            'serviced_by': self.engineer.id
        }
        response = self.client.post(reverse('visits:visit_create_view',
                    kwargs={'id':self.allocation.id}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Failed', response.content)


    def test_visit_create_view_post_invalid_allocatedcall_id(self):
        self.client.force_login(self.user)
        data = {
            'serviced_by': self.engineer.id,
            'visit_status': 'CNA',
            'visit_date_time': datetime.datetime.now(),
            'outcome': 'Nice',
            'call_status': 'Open',
            'call_status_final': False,
            'call_visit_final_notes': 'Ok Report'
        }
        response = self.client.post(reverse('visits:visit_create_view',
                    kwargs={'id':self.allocation.id + 1}), data, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Not Found', response.content)


    def test_visit_detail_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('visits:visit_detail_view',
                                kwargs={'id':self.visit.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visits/visit_detail_view.html')
        self.assertIn(b'Lorem ipsum dolor', response.content)
        self.assertIn(b'Revisit required', response.content)
        self.assertIn(b'GoGo Go', response.content)
        self.assertIn(b'Wet Service Required', response.content)


    def test_visit_detail_view_invalid_id(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('visits:visit_detail_view',
                                kwargs={'id':self.visit.id + 1}))
        self.assertEqual(response.status_code, 404)
