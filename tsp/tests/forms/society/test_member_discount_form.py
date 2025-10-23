"""Unit tests of the member discount form"""
from django.test import TestCase
from tsp.forms.society.member_discount_form import MemberDiscountForm
from tsp.models import Society

class MemberDiscountFormTestCase(TestCase):
    """Unit tests of the member discount form"""
    
    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.form_input={'member_discount':50.00}

    def test_valid_form(self):
        form = MemberDiscountForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_necessary_fileds(self):
        form = MemberDiscountForm()
        self.assertIn('member_discount', form.fields)

    def test_blank_field(self):
        self.form_input['member_discount'] = ''
        form = MemberDiscountForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_percentage_must_not_be_negative(self):
        self.form_input['member_discount'] = '-45.00'
        form = MemberDiscountForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_percentage_must_be_less_than_or_equal_to_hundred(self):
        self.form_input['member_discount'] = '130.00'
        form = MemberDiscountForm(data=self.form_input)
        self.assertFalse(form.is_valid())