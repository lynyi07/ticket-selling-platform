"""Unit Tests of the forgot password form"""
from django.test import TestCase
from tsp.forms.forgot_password_form import ForgetPasswordForm 

class ForgotPasswordFormTestCase(TestCase): 
    """Unit Tests of the forgot password form"""

    def setUp(self):
        self.form_input = {'email': "johndoe@kcl.ac.uk"} 

    def test_form_has_required_fields(self): 
        form = ForgetPasswordForm() 
        self.assertIn("email", form.fields) 
         
    def form_accepts_valid_data(self): 
        form = ForgetPasswordForm(data=self.form_input) 
        self.assertTrue(form.is_valid()) 

    def test_get_email_with_valid_email(self): 
        form = ForgetPasswordForm(data=self.form_input) 
        self.assertEqual(form.get_email(), "johndoe@kcl.ac.uk")

    def test_get_email_with_invalid_email(self):
        self.form_input['email'] = 'john'
        form = ForgetPasswordForm(data=self.form_input) 
        self.assertEqual(form.get_email(), None)

    def test_email_must_not_be_blank(self): 
        self.form_input['email'] = ''
        form = ForgetPasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())