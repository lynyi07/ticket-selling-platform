"""Unit tests of the sign up form"""
from django import forms
from django.test import TestCase
from tsp.forms.sign_up_form import SignUpForm
from tsp.models import Student

class SignUpFormTestCase(TestCase):
    """Unit tests of the sign up form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.form_input = {
            "first_name": "John",
            "last_name": "Smith",
            "email":"k21034100@kcl.ac.uk",
            "password":"Password123",
            "password_confirmation":"Password123",
        }

    def test_valid_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        before_count = Student.objects.count()
        form.save()
        after_count = Student.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        self.assertIn('password_confirmation', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        password_field_widget = form.fields['password'].widget
        self.assertTrue(isinstance(password_field_widget, forms.PasswordInput))
        password_confirmation_field_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_field_widget, forms.PasswordInput))

    def test_blank_first_name(self):
        self.form_input['first_name'] = ''
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_last_name(self):
        self.form_input['last_name'] = ''
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_email(self):
        self.form_input['email'] = ''
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_password(self):
        self.form_input['password'] = ''
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_password_confirmation(self):
        self.form_input['password_confirmation'] = ''
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_invalid_email_input(self):
        self.form_input['email'] = 'k21034100@wrong.domain'
        form = SignUpForm(data = self.form_input)
        self.assertIn('Email is not associated with any university', form.errors['email'])
        self.assertFalse(form.is_valid())

    def test_email_already_exists(self):
        self.form_input['email'] = 'johndoe@kcl.ac.uk'
        form = SignUpForm(data = self.form_input)
        self.assertIn('Student already exists', form.errors['email'])
        self.assertFalse(form.is_valid())

    def test_password_must_contain_an_uppercase_letter(self):
        self.form_input['password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_a_lowercase_letter(self):
        self.form_input['password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_a_number(self):
        self.form_input['password'] = 'PasswordPassword'
        self.form_input['password_confirmation'] = 'PasswordPassword'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_be_at_least_8_characters_long(self):
        self.form_input['password'] = 'Pass123'
        self.form_input['password_confirmation'] = 'Pass123'
        form = SignUpForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_and_password_confirmation_must_be_equal(self):
        self.form_input['password'] = 'Password123'
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data = self.form_input)
        self.assertIn('Password does not match', form.errors['password_confirmation'])
        self.assertFalse(form.is_valid())