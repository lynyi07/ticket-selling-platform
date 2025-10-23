"""Unit tests of sign up view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from tsp.forms.sign_up_form import SignUpForm
from tsp.models import Student, University
from ..helpers import LoginTester
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from tsp.views.tokens import account_activation_token

class SignUpViewTestCase(TestCase, LoginTester):
    """Unit tests of sign up view"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email":"janedoe@kcl.ac.uk",
            "password":"Password123",
            "password_confirmation":"Password123",
        }

    def test_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')   # Check whether correct template has been used
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'notemail'
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)             #checks if number of students is the same
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_sign_up(self):
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count + 1)             #checks if number of students has increased by one
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        student = Student.objects.get(email = 'janedoe@kcl.ac.uk')       # Validating student's details
        self.assertEqual(student.first_name, 'Jane')
        self.assertEqual(student.last_name, 'Smith')
        self.assertEqual(student.email, 'janedoe@kcl.ac.uk')
        check_password('Password123', student.password)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate your user account')
        self.assertEqual(mail.outbox[0].to, ['janedoe@kcl.ac.uk'])
        self.assertFalse(self._is_logged_in())

    def test_successful_activate_account_email(self):
        student = Student.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="janedoe@kcl.ac.uk",
            password="Password123",
            university = University.objects.get(name="King's College London"),
            role = "STUDENT",
            is_superuser = False,
        )
        student.is_active = False
        student.save()
        uid = urlsafe_base64_encode(force_bytes(student.pk))
        token = account_activation_token.make_token(student)
        url = reverse('activate', kwargs={'uidb64':uid, 'token':token})
        response = self.client.get(url, follow=True)
        redirected_url = reverse('login')
        self.assertRedirects(response, redirected_url, 302, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertTrue(Student.objects.get(email='janedoe@kcl.ac.uk').is_active)

    def test_unsuccessful_activate_account_email(self):
        student = Student.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="janedoe@kcl.ac.uk",
            password="Password123",
            university = University.objects.get(name="King's College London"),
            role = "STUDENT",
            is_superuser = False,
        )
        student.is_active = False
        student.save()
        uid = urlsafe_base64_encode(force_bytes(0))
        token = account_activation_token.make_token(student)
        url = reverse('activate', kwargs={'uidb64':uid, 'token':token})
        response = self.client.get(url, follow=True)
        redirected_url = reverse('sign_up')
        self.assertRedirects(response, redirected_url, 302, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_get_sign_up_redirects_when_logged_in(self):
        self.client.login(email = 'johndoe@kcl.ac.uk', password = 'Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_user_cannot_login_before_activation(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertFalse(LoginTester._is_logged_in(self))