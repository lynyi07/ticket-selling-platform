"""Unit tests of the add to cart form"""
from django.test import TestCase
from django import forms
from tsp.models import User, Society, Student, Event, Cart, EventCartItem
from tsp.forms.student.add_to_cart_form import AddToCartForm

class AddToCartFormTestCase(TestCase):
    """Unit tests of the add to cart form"""

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
        # The default cart contains 2 early bird tickets of the default event 
        # and the membership of the default society membership
        self.cart = Cart.objects.get(student=self.student)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.default_society = Society.objects.get(email='tech_society@kcl.ac.uk')
        # Set another society to organise the given event together with the 
        # default society
        self.other_society = Society.objects.get(email='ai_society@kcl.ac.uk')
        self.event.society.add(self.other_society)
        self.form_input = {
            'early_bird_to_add': 2,
            'standard_to_add': '',
            'membership': self.other_society,
        }      
        
    def test_valid_form(self):
        form = AddToCartForm(user=self.user, event=self.event, data=self.form_input)
        self.assertTrue(form.is_valid())  
    
    def test_form_has_necessary_fields(self):
        form = AddToCartForm(user=self.user, event=self.event)
        self.assertIn('early_bird_to_add', form.fields)
        self.assertIn('standard_to_add', form.fields)
        self.assertIn('membership', form.fields)

    def test_membership_options(self):
        form = AddToCartForm(user=self.user, event=self.event)
        # Count the number of societies that accept new members
        society_count = sum(
            1 for society in self.event.society.all()
            if society.accept_new_member 
        )
        self.assertEqual(len(form.fields['membership'].choices), society_count + 1)
        self.assertEqual(form.fields['membership'].choices[0][0], '')
        # Test the society that is accepting new members is listed as 
        # a membership option
        self.assertTrue(self.default_society.accept_new_member)
        self.assertIn(
            str(self.default_society .pk),
            [choice[0] for choice in form.fields['membership'].choices]
        )
        # Test the society that is not accepting new members is not listed 
        # as a membership option
        self.other_society.stripe_account_id = ''
        self.other_society.save()
        form = AddToCartForm(user=self.user, event=self.event)
        self.assertFalse(self.other_society.accept_new_member)
        self.assertNotIn(
            str(self.other_society .pk),
            [choice[0] for choice in form.fields['membership'].choices]
        )

    def test_membership_labels(self):
        form = AddToCartForm(user=self.user, event=self.event)
        self.assertEqual(form.fields['membership'].choices[0][1], '-----')
        default_society_label = f'{self.default_society.name} £{self.default_society.member_fee}'
        self.assertEqual(
            form.fields['membership'].choices[1][1], 
            default_society_label
        )
        other_society_label = f'{self.other_society .name} £{self.other_society.member_fee}'
        self.assertIn(
            other_society_label,
            [choice[1] for choice in form.fields['membership'].choices]
        )
    
    def test_ticket_options_when_both_ticket_types_available(self):
        self.cart.clear()
        form = AddToCartForm(user=self.user, event=self.event)
        form._set_ticket_options()
        # Test early bird ticket options
        early_booking_capacity = self.event.early_booking_capacity 
        self.assertFalse(form.fields['early_bird_to_add'].widget.attrs['disabled'])
        self.assertEqual(form.fields['early_bird_to_add'].label, 'Early Bird Ticket')    
        number_of_options = len(form.fields['early_bird_to_add'].choices)
        self.assertEqual(number_of_options, early_booking_capacity)
        # Test the first option and last option of early bird tickets
        self.assertEqual(form.fields['early_bird_to_add'].choices[0], (1, '1'))
        self.assertEqual(
            form.fields['early_bird_to_add'].choices[number_of_options-1], 
            (number_of_options, f'{number_of_options}')
        )
        # Test standard ticket options
        self.assertTrue(form.fields['standard_to_add'].widget.attrs['disabled'])
        self.assertEqual(
            form.fields['standard_to_add'].label, 
            'Standard Ticket (Not Released)'
        )
        number_of_options = len(form.fields['standard_to_add'].choices)
        self.assertEqual(number_of_options, 1) 
        self.assertEqual(form.fields['standard_to_add'].choices[0], ('', '-----'))
    
    def test_ticket_options_when_only_standard_ticket_available(self):
        # Test early bird ticket option updates when all available early bird
        # tickets are added to cart.
        self.cart.clear()
        early_booking_capacity = self.event.early_booking_capacity 
        self._add_ticket_to_cart(early_booking_capacity, 0)
        form = AddToCartForm(user=self.user, event=self.event)
        form._set_ticket_options()
        self.assertTrue(form.fields['early_bird_to_add'].widget.attrs['disabled'])
        self.assertEqual(
            form.fields['early_bird_to_add'].label, 
            'Early Bird Ticket (Sold Out)'
        )
        self.assertEqual(len(form.fields['early_bird_to_add'].choices), 1) 
        self.assertEqual(form.fields['early_bird_to_add'].choices[0], ('', '-----'))
        # Test standard ticket option updates when all early bird tickets are
        # sold out.
        standard_booking_capacity = self.event.standard_booking_capacity 
        self.assertFalse(form.fields['standard_to_add'].widget.attrs['disabled'])
        self.assertEqual(form.fields['standard_to_add'].label, 'Standard Ticket')
        number_of_options = len(form.fields['standard_to_add'].choices)
        self.assertEqual(number_of_options, standard_booking_capacity)
        # Test the first option and last option of standard tickets
        self.assertEqual(form.fields['standard_to_add'].choices[0], (1, '1'))
        self.assertEqual(
            form.fields['standard_to_add'].choices[number_of_options-1], 
            (number_of_options, f'{number_of_options}')
        )
        
    def test_ticket_options_when_both_types_are_not_available(self):
        # Add all early bird tickets and standard tickets to cart
        self.cart.clear()
        early_booking_capacity = self.event.early_booking_capacity 
        standard_booking_capacity = self.event.standard_booking_capacity 
        self._add_ticket_to_cart(early_booking_capacity, standard_booking_capacity)
        form = AddToCartForm(user=self.user, event=self.event)
        form._set_ticket_options()
        # Test early bird ticket option and standard ticket option update correctly.
        self.assertTrue(form.fields['early_bird_to_add'].widget.attrs['disabled'])
        self.assertEqual(form.fields['early_bird_to_add'].label, 'Early Bird Ticket (Sold Out)')
        self.assertEqual(len(form.fields['early_bird_to_add'].choices), 1)
        self.assertEqual(form.fields['early_bird_to_add'].choices[0], ('', '-----'))
        self.assertTrue(form.fields['standard_to_add'].widget.attrs['disabled'])
        self.assertEqual(form.fields['standard_to_add'].label, 'Standard Ticket (Sold Out)')
        self.assertEqual(len(form.fields['standard_to_add'].choices), 1)
        self.assertEqual(form.fields['standard_to_add'].choices[0], ('', '-----'))
        
    def _add_ticket_to_cart(self, early_bird_to_add, standard_to_add):
        self.event_cart_item.early_bird_quantity = early_bird_to_add
        self.event_cart_item.standard_quantity = standard_to_add
        self.event_cart_item.save()
        self.cart.event_cart_item.add(self.event_cart_item)
    
    def test_must_not_add_membership_if_already_a_member(self):
        self.default_society.add_regular_member(self.student)
        self.form_input['membership'] = self.default_society
        data = self.form_input
        form = AddToCartForm(user=self.user, event=self.event, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('membership', form.errors)
        self.assertEqual(form.errors['membership'][0], 'You are already a member.')

    def test_must_not_add_membership_if_already_in_cart(self):
        self.cart.membership.add(self.default_society)
        self.form_input['membership'] = self.default_society
        data = self.form_input
        form = AddToCartForm(user=self.user, event=self.event, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('membership', form.errors)
        self.assertEqual(form.errors['membership'][0], 'You can only add it once.')

    def test_update_cart_by_adding_membership(self):
        form = AddToCartForm(user=self.user, event=self.event)
        form.update_cart(self.other_society )
        self.assertIn(self.other_society , self.cart.membership.all())