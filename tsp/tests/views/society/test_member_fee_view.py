"""Unit tests of the member fee view"""
from django.test import TestCase
from tsp.models import Society
from django.urls import reverse
from tsp.forms.society.member_fee_form import MemberFeeForm
from tsp.tests.helpers import reverse_with_next

class MemberFeeViewTestCase(TestCase):
    """Unit tests of the member fee view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('member_fee')
        self.form_input = { 'member_fee': 50.00 }

    def test_request_url(self):
        self.assertEqual(self.url, '/member_fee/')

    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/member_fee.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MemberFeeForm))
    
    def test_get_request_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_member_fee_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_member_fee_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_successful_update_member_fee(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('member_fee')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'society/member_fee.html')
        self.user.refresh_from_db()      
        is_updated = (self.user.member_fee==self.form_input['member_fee'])
        self.assertTrue(is_updated)
    
    def test_successful_update_member_fee_to_0(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['member_fee'] = 0
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('member_fee')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'society/member_fee.html')
        self.user.refresh_from_db()      
        is_updated = (self.user.member_fee==self.form_input['member_fee'])
        self.assertTrue(is_updated)

    def test_unsuccessful_update_member_fee(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['member_fee'] = -5
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/member_fee.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MemberFeeForm))
        self.assertTrue(form.is_bound)
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        regular_member_url = reverse('list_regular_member')
        self.assertContains(response, regular_member_url)