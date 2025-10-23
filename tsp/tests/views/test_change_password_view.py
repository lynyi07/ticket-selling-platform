"""Unit tests of the change password view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from tsp.forms.change_password_form import ChangePasswordForm
from tsp.models import Student
from ..helpers import LoginTester
from tsp.tests.helpers import reverse_with_next

class ChangePasswordViewTestCase(TestCase, LoginTester):
    """Unit tests of the change password view"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_user.json'
    ]
    
    def setUp(self):
        self.user = Student.objects.get(email = 'johndoe@kcl.ac.uk')
        self.url = reverse('change_password')
        self.form_input = {
            "password": "Password123",
            "new_password": "NewPassword123",
            "password_confirmation":"NewPassword123",
        }

    def test_url(self):
        self.assertEqual(self.url, '/change_password/')

    def test_get_change_password(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')   # Check whether correct template has been used
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_change_password(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['new_password'] = 'wrongpassword'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.assertTrue(form.is_bound)
        self.assertTrue(self._is_logged_in())

    def test_successful_change_password(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('change_password')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'change_password.html')
        self.user.refresh_from_db()       # Validating student's details
        is_password_correct = check_password('NewPassword123', self.user.password)
        self.assertTrue(self._is_logged_in())
        self.assertTrue(is_password_correct)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_get_change_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)