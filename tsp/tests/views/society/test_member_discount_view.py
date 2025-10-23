"""Unit tests of the member discount view"""
from django.test import TestCase
from tsp.models import Society
from django.urls import reverse
from tsp.forms.society.member_discount_form import MemberDiscountForm
from tsp.tests.helpers import reverse_with_next

class MemberDiscountViewTestCase(TestCase):
    """Unit tests of the member discount view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('member_discount')
        self.form_input = { 'member_discount': 50.00 }

    def test_request_url(self):
        self.assertEqual(self.url, '/member_discount/')

    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/member_discount.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MemberDiscountForm))
    
    def test_get_request_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_member_discount_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_member_discount_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_successful_update_member_discount(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('member_discount')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'society/member_discount.html')
        self.user.refresh_from_db()      
        is_updated = (self.user.member_discount==self.form_input['member_discount'])
        self.assertTrue(is_updated)
    
    def test_successful_update_member_discount_to_0(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['member_discount'] = 0
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('member_discount')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'society/member_discount.html')
        self.user.refresh_from_db()      
        is_updated = (self.user.member_discount==self.form_input['member_discount'])
        self.assertTrue(is_updated)

    def test_unsuccessful_update_member_discount(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['member_discount'] = -69
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/member_discount.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MemberDiscountForm))
        self.assertTrue(form.is_bound)
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        regular_member_url = reverse('list_regular_member')
        self.assertContains(response, regular_member_url)