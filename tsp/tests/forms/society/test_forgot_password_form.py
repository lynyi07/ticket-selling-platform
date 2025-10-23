"""Unit tests of the forgot password form"""
from django import forms
from django.test import TestCase
from tsp.forms.forgot_password_form import ForgetPasswordForm 

class ForgotPasswordFormTestCase(TestCase):
    """Unit tests of the forgot password form"""

    def setUp(self): 
        self.form_input = {"email": "k21034100@kcl.ac.uk"} 

    def test_valid_form(self): 
        form = ForgetPasswordForm(data=self.form_input) 
        self.assertTrue(form.is_valid()) 

    def test_necessary_fields(self): 
        form = ForgetPasswordForm() 
        self.assertIn('email', form.fields) 
        email_field = form.fields['email'] 
        self.assertTrue(isinstance(email_field, forms.EmailField)) 

    def test_get_email(self): 
        form = ForgetPasswordForm(data=self.form_input) 
        self.assertTrue(self.form_input.get("email") == form.get_email())