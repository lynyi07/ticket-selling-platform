"""Unit tests of the login form"""
from django import forms
from django.test import TestCase
from tsp.forms.login_form import LogInForm

class LogInFormTestCase(TestCase): 
    """Unit tests of the login form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ] 

    def setUp(self): 
        self.form_input = {'email': 'johndoe@kcl.ac.uk', 'password': 'Password123'} 

    def test_form_contains_required_fields(self):
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget,forms.PasswordInput)) 

    def test_form_accepts_valid_input(self):
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid()) 

    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid()) 

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid()) 

    def test_form_accepts_incorrect_username(self):
        self.form_input['email'] = 'hello@kcl.ac.uk'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid()) 

    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = 'pwd'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid()) 

    def test_blank_email_does_not_authenticate(self):
        form_input = {'email': '', 'password': 'Password123'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None) 

    def test_blank_password_does_not_authenticate(self):
        form_input = {'username': 'johndoe@kcl.ac.uk', 'password': ''}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)