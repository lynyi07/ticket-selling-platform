"""Unit tests of the bank details view"""
from django.test import TestCase
from tsp.models import Society
from tsp.tests.helpers import reverse_with_next
from tsp.forms.society.bank_details_form import BankDetailsForm
from tsp.views.society.bank_details_view import BankDetailsView
from django.urls import reverse
from django.contrib.messages import get_messages
import stripe

class BankDetailsViewTestCase(TestCase):
    """Unit tests of the bank details view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json'
    ]
    
    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('bank_details')
        self.form_input = {
            "account_number": "00012345",
            "sort_code": "040004",
            "account_name":"John Doe"
        }
    
    def test_bank_details_url(self):
        self.assertEqual(self.url, '/bank_details/')
        
    def test_get_bank_details_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200) 
    
    def test_get_bank_details_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_bank_details_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html') 
    
    def test_get_object(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        view = response.context['view']
        obj = view.get_object()
        self.assertEqual(obj, self.user)

    def test_successful_set_bank_details(self):
        self.user.stripe_account_id = ''
        self.user.save()
        self.client.login(email=self.user.email, password='Password123')
        form_data = self.form_input
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        # Test stripe account is created and terms are accepted
        self.assertIsNotNone(self.user.stripe_account_id)
        account = stripe.Account.retrieve(self.user.stripe_account_id)
        self.assertIsNotNone(account.tos_acceptance.ip)
        self.assertIsNotNone(account.tos_acceptance.date)
        # Test bank details are set correctly
        expected_account_number = form_data['account_number']
        expected_sort_code = form_data['sort_code']
        expected_account_name = form_data['account_name']
        actual_account_number = self.user.account_number
        actual_sort_code = self.user.sort_code
        actual_account_name = self.user.account_name    
        self.assertEqual(expected_account_number, actual_account_number)
        self.assertEqual(expected_sort_code, actual_sort_code)
        self.assertEqual(expected_account_name, actual_account_name)
        # Test success message is displayed
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1) 
        self.assertEqual(str(messages[0]), "Bank details updated successfully!")
    
    def test_update_bank_details_on_existing_account(self):
        self.user.stripe_account_id = 'acct_1MfrHlKvlxSITsBd'
        self.user.save()
        self.client.login(email=self.user.email, password='Password123')
        form_data = self.form_input
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        # Test bank details are updated correctly
        expected_account_number = form_data['account_number']
        expected_sort_code = form_data['sort_code']
        expected_account_name = form_data['account_name']
        actual_account_number = self.user.account_number
        actual_sort_code = self.user.sort_code
        actual_account_name = self.user.account_name    
        self.assertEqual(expected_account_number, actual_account_number)
        self.assertEqual(expected_sort_code, actual_sort_code)
        self.assertEqual(expected_account_name, actual_account_name)
        # Test success message is displayed
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1) 
        self.assertEqual(str(messages[0]), "Bank details updated successfully!")
            
    def test_unsuccessful_set_bank_details(self):
        self.client.login(email=self.user.email, password='Password123')
        form_data = {
            'bank_account': '12345678',
            'sort_code': '12345',
            'account_name': self.user.name,
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Failed to update bank details.")