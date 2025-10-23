"""Unit tests of the EventCartItem model"""
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from tsp.models import Event, EventCartItem, Society
    
class EventCartItemModelTestCase(TestCase):
    """Unit tests of the EventCartItem model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]

    def setUp(self):
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.event = Event.objects.get(name='Default test event')
        self.society = Society.objects.get(pk=5)
        
    def test_event_cart_item_has_event(self):
        self.assertEqual(self.event_cart_item.event, self.event)
    
    def test_event_cart_item_has_early_bird_quantity(self):
        self.assertEqual(self.event_cart_item.early_bird_quantity, 2)
    
    def test_event_cart_item_has_standard_quantity(self):
        self.assertEqual(self.event_cart_item.standard_quantity, 0)
        
    def test_event_cart_item_early_bird_quantity_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            self.event_cart_item.early_bird_quantity = -1
            self.event_cart_item.full_clean()
            
    def test_event_cart_item_standard_quantity_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            self.event_cart_item.standard_quantity = -1
            self.event_cart_item.full_clean()
            
    def test_get_discount_amount_with_early_bird_quantity(self):
        discount_rate = self.society.member_discount
        expected_discount_amount = self.event.early_bird_price * discount_rate
        # Set standard quantity to 0 to ensure the discount will be applied to 
        # early bird price.
        self.event_cart_item.standard_quantity = 0
        self.event_cart_item.save()
        actual_discount_amount = self.event_cart_item.get_discount_amount(discount_rate)
        self.assertEqual(expected_discount_amount, actual_discount_amount)
    
    def test_get_discount_amount_with_standard_quantity(self):
        # Test discount will apply to standard ticket if it is in cart.
        self.event_cart_item.standard_quantity = 2
        self.event_cart_item.save()
        discount_rate = self.society.member_discount
        expected_discount_amount = self.event.standard_price * discount_rate
        actual_discount_amount = self.event_cart_item.get_discount_amount(discount_rate)
        self.assertEqual(expected_discount_amount, actual_discount_amount)
    
