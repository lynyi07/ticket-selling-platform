"""Unit tests of the bank details form"""
from django.test import TestCase
from tsp.forms.society.bank_details_form import BankDetailsForm

class BankDetailsFormTestCase(TestCase):
    """Unit tests of the bank details form"""

    def setUp(self):
        self.form_input = {
            "account_number": "00012345",
            "sort_code": "040004",
            "account_name":"John Doe"
        }

    def test_necessary_fields(self):
        form = BankDetailsForm()
        self.assertIn('account_number', form.fields)
        self.assertIn('sort_code', form.fields)
        self.assertIn('account_name', form.fields)

    def test_valid_form(self):
        form = BankDetailsForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_blank_account_number(self):
        self.form_input['account_number'] = ''
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Account number must not be empty.', form.errors['account_number'])
        self.assertFalse(form.is_valid())
    
    def test_blank_sort_code(self):
        self.form_input['sort_code'] = ''
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Sort code must not be empty.', form.errors['sort_code'])
        self.assertFalse(form.is_valid())

    def test_blank_account_name(self):
        self.form_input['account_name'] = ''
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Account name must not be empty.', form.errors['account_name'])
        self.assertFalse(form.is_valid())

    def test_account_number_contains_letters(self):
        self.form_input['account_number'] = 'abcdefgh'
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Account number must contain only digits.', form.errors['account_number'])
        self.assertFalse(form.is_valid())

    def test_sort_code_contains_letters(self):
        self.form_input['sort_code'] = 'abcdef'
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Sort code must contain only digits.', form.errors['sort_code'])
        self.assertFalse(form.is_valid())

    def test_sort_code_is_not_6_digits(self):
        self.form_input['sort_code'] = '111'
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Sort code must be 6 digits.', form.errors['sort_code'])
        self.assertFalse(form.is_valid())

    def test_account_number_is_not_8_digits(self):
        self.form_input['account_number'] = '111'
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Account number must be 8 digits.', form.errors['account_number'])
        self.assertFalse(form.is_valid())
    
    def test_account_name_contains_digits(self):
        self.form_input['account_name'] = '111'
        form = BankDetailsForm(data = self.form_input)
        self.assertIn('Account name should not contain digits.', form.errors['account_name'])
        self.assertFalse(form.is_valid())