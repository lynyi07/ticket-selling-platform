"""Unit tests of the update cart form"""
from django.test import TestCase
from django import forms
from tsp.models import User, Society, Student, Event, Cart, EventCartItem
from tsp.forms.student.update_cart_form import UpdateCartForm

class AddToCartFormTestCase(TestCase):
    """Unit tests of the update cart form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]
    
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.student = self.user.student
        self.event = Event.objects.get(pk=15)
        self.cart = Cart.objects.get(student=self.student)
        self.society = Society.objects.get(email='ai_society@kcl.ac.uk')
        self.event.society.add(self.society)
        self.form_input = {
            'membership': self.society,
        }      
        
    def test_valid_form(self):
        form = UpdateCartForm(data=self.form_input, user=self.user, membership=self.society)
        self.assertTrue(form.is_valid())  

    def test_form_has_necessary_fields(self):
        form = UpdateCartForm()
        self.assertIn('membership', form.fields) 
    
    def test_membership_field_initialization(self):
        form = UpdateCartForm(event=self.event, user=self.user, membership=self.society)
        self.assertEqual(form.fields['membership'].queryset.first(), self.society)
        self.assertEqual(form.fields['membership'].initial, self.society) 
    
    def test_update_cart_by_removing_membership(self):
        # Test that when the membership field is specified, the given membership 
        # is removed from the cart
        self.cart.membership.add(self.society)
        self.assertIn(self.society, self.cart.membership.all())
        form = UpdateCartForm(data=self.form_input, user=self.user, membership=self.society)
        self.assertTrue(form.is_valid())
        cart = form.save()
        self.assertNotIn(self.society, cart.membership.all())
   