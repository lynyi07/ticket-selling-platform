"""Unit tests of the member fee form"""
from django.test import TestCase
from tsp.forms.society.member_fee_form import MemberFeeForm
from tsp.models import Society

class MemberFeeFormTestCase(TestCase):
    """Unit tests of the member fee form"""
    
    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.form_input={'member_fee':50.00}

    def test_valid_form(self):
        form = MemberFeeForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_necessary_fileds(self):
        form = MemberFeeForm()
        self.assertIn('member_fee', form.fields)

    def test_blank_field(self):
        self.form_input['member_fee'] = ''
        form = MemberFeeForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_member_fee_must_not_be_negative(self):
        self.form_input['member_fee'] = '-45.00'
        form = MemberFeeForm(data=self.form_input)
        self.assertFalse(form.is_valid())