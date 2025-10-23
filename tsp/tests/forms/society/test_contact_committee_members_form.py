"""Unit tests of the contact committee member form"""
from django.test import TestCase
from tsp.forms.society.contact_members_form import ContactCommitteeMembersForm
from django import forms

class ContactCommitteeFormTestCase(TestCase):
    """Unit tests of the contact committee member form""" 

    def setUp(self): 
        self.form_input = {
            'email_header': 'Test Email',
            'email_message': 'This is a test email.'
        } 

    def test_valid_form(self): 
        form = ContactCommitteeMembersForm(data=self.form_input) 
        self.assertTrue(form.is_valid)

    def test_necessary_fields(self): 
        form = ContactCommitteeMembersForm() 
        self.assertIn('email_header', form.fields)
        self.assertIn('email_message', form.fields)
        self.assertTrue(isinstance(form.fields['email_header'].widget, forms.widgets.TextInput))
        self.assertTrue(isinstance(form.fields['email_message'].widget, forms.widgets.Textarea))

    def test_blank_email_header(self): 
        self.form_input['email_header'] = '' 
        form = ContactCommitteeMembersForm(data=self.form_input) 
        self.assertFalse(form.is_valid()) 

    def test_blank_email_message(self): 
        self.form_input['email_message'] = '' 
        form = ContactCommitteeMembersForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_get_header_with_a_valid_email_header(self):
        form = ContactCommitteeMembersForm(data=self.form_input)
        self.assertEqual(self.form_input['email_header'], form.get_header())

    def test_get_header_with_an_invalid_email_header(self):
        self.form_input['email_header'] = ''
        form = ContactCommitteeMembersForm(data=self.form_input)
        self.assertEqual(None, form.get_header())

    def test_get_message_with_a_valid_email_message(self):
        form = ContactCommitteeMembersForm(data=self.form_input)
        self.assertEqual(self.form_input['email_message'], form.get_message())

    def test_get_message_with_an_invalid_email_message(self):
        self.form_input['email_message'] = ''
        form = ContactCommitteeMembersForm(data=self.form_input)
        self.assertEqual(None, form.get_message())