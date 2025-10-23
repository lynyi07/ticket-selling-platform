"""Unit tests of log in view"""
from django.test import TestCase
from django.urls import reverse
from tsp.forms.login_form import LogInForm
from tsp.tests.helpers import LoginTester
from tsp.models import Student, Society

class LoginViewTestCase(TestCase, LoginTester):
    """Unit tests of log in view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.url = reverse('login')
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')

    def test_log_in_url(self):
        self.assertEqual(self.url,'/login/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)

    def test_log_in_with_blank_username(self):
        form_input = { 'email': '', 'password': 'Password123', 'account':'STUDENT'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(LoginTester._is_logged_in(self))

    def test_unsuccesful_log_in(self):
        form_input = { 'email': '@JohnDoe', 'password': 'WrongPassword123', 'account':'STUDENT' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(LoginTester._is_logged_in(self))
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_log_in_with_blank_password(self):
        form_input = { 'email': 'johndoe@kcl.ac.uk', 'password': '' , 'account':'STUDENT'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(LoginTester._is_logged_in(self))

    def test_succesful_log_in(self):
        form_input = { 'email': 'johndoe@kcl.ac.uk', 'password': 'Password123', 'account':'STUDENT' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(LoginTester._is_logged_in(self))
        response_url = reverse('landing')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_succesful_log_in_with_redirect(self):
        redirect_url = reverse('landing')
        form_input = { 'email': 'johndoe@kcl.ac.uk', 'password': 'Password123', 'next': redirect_url, 'account':'STUDENT'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(LoginTester._is_logged_in(self))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_succesful_log_in_with_redirect_for_society_account(self):
        redirect_url = reverse('edit_profile_page')
        form_input = { 'email': 'tech_society@kcl.ac.uk', 'password': 'Password123', 'next': redirect_url , 'account':'SOCIETY'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'society/edit_profile_page.html')

    def test_get_log_in_redirects_when_logged_in(self):
        self.client.login(email = 'johndoe@kcl.ac.uk', password = 'Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html') 