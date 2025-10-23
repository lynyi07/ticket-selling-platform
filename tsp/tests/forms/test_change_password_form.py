"""Unit tests of the change password form"""
from django.test import TestCase
from tsp.models import Student
from tsp.forms.change_password_form import ChangePasswordForm

class ChangePasswordFormTestCase(TestCase):
    """Unit tests of the change password form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email = 'johndoe@kcl.ac.uk')
        self.form_input = {
            'new_password' : 'Pw12345678910',
            'password_confirmation' : 'Pw12345678910'
        }

    def test_form_has_necessary_fields(self):
        form = ChangePasswordForm()
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_valid_form(self):
        form = ChangePasswordForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_blank_first_name(self):
        self.form_input['new_password'] = ''
        form = ChangePasswordForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_password_confirmation(self):
        self.form_input['password_confirmation'] = ''
        form = ChangePasswordForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PW12345678910'
        self.form_input['confirmation_password'] = 'PW12345678910'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'pw12345678910'
        self.form_input['confirmation_password'] = 'pw12345678910'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['password'] = 'Abcdefgh'
        self.form_input['password_confirmation'] = 'Abcdefgh'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_not_be_less_than_8_characters(self):
        self.form_input['password'] = 'Pw123'
        self.form_input['password_confirmation'] = 'Pw123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = "Pw12345678"
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())