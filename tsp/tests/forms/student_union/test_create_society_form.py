"""Unit tests of the create society form"""
from django import forms
from django.test import TestCase
from tsp.forms.student_union.create_society_form import CreateSocietyForm

class CreateSocietyFormTestCase(TestCase):
    """Unit tests of the create society form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
    ]

    def setUp(self):
        self.form_input = {
            "name": "AI",
            "email": "aisoc@kcl.ac.uk",
        }

    def test_valid_form(self):
        form = CreateSocietyForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_necessary_fields(self):
        form = CreateSocietyForm()
        self.assertIn('name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_blank_name(self):
        self.form_input['name'] = ''
        form = CreateSocietyForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_email(self):
        self.form_input['email'] = ''
        form = CreateSocietyForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_invalid_email_input(self):
        self.form_input['email'] = 'k21034100@wrong.domain'
        form = CreateSocietyForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_email_already_exists(self):
        self.form_input['email'] = 'tech_society@kcl.ac.uk'
        form = CreateSocietyForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_name_already_exists(self):
        self.form_input['name'] = 'Tech society'
        form = CreateSocietyForm(data = self.form_input)
        self.assertFalse(form.is_valid())