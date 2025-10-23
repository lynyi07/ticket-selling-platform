"""Unit tests of the Forgot Password view"""
from django.test import TestCase
from django.urls import reverse
from tsp.forms.forgot_password_form import ForgetPasswordForm
from tsp.tests.helpers import reverse_with_next
from django.core import mail

class ForgotPasswordViewTestCase(TestCase): 

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ] 

    def setUp(self):
        self.form_input = {
            'email': 'johndoe@kcl.ac.uk'
        }
        self.url = reverse('forgot_password') 

    def test_request_url(self): 
        self.assertEqual(self.url,'/forgot_password/') 

    def test_get_forgot_password(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot_password.html')   # Check whether correct template has been used
        form = response.context['form']
        self.assertTrue(isinstance(form, ForgetPasswordForm))

    def test_post_forgot_password_with_valid_data(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('forgot_password')
        self.assertRedirects(response, redirect_url, 302, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Request')
        self.assertEqual(mail.outbox[0].to, ['johndoe@kcl.ac.uk'])
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_post_forgot_password_with_invalid_email(self):
        self.form_input['email'] = 'WrongEmail@kcl.ac.uk'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(len(mail.outbox), 0)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_post_forgot_password_with_blank_email(self):
        self.form_input['email'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(len(mail.outbox), 0)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_get_forgot_password_redirects_when_logged_in(self):
        self.client.login(email = 'johndoe@kcl.ac.uk', password = 'Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html') 