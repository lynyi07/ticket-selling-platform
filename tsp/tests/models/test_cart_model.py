"""Unit tests of the Cart model"""
from django.test import TestCase
from tsp.models import Event, EventCartItem, Cart, Society, Student
from decimal import Decimal
from collections import defaultdict

class CartModelTestCase(TestCase):
    """Unit tests of the Cart model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        # There are 2 early bird tickets and 1 associated society membership 
        # in cart.
        self.cart = self.student.cart
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.event = self.event_cart_item.event
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')
        
    def test_cart_owner(self):
        self.assertEqual(self.cart.student, self.student)
       
    def test_all_items_free(self):
        # Test when there are items in the cart and all items are free.
        self.event.early_bird_price = 0
        self.event.save()
        self.society.member_fee = 0
        self.society.save()
        self.assertTrue(self.cart.count > 0)
        self.assertTrue(self.cart.total_price == 0)
        self.assertTrue(self.cart.all_items_free)
        # Test when there are some items in the cart that are not free.
        self.event.early_bird_price = Decimal('10.00')
        self.event.save()
        self.society.member_fee = Decimal('10.00')
        self.society.save()
        self.assertFalse(self.cart.all_items_free)
    
    def test_total_price(self):        
        # Test when there are some items in the cart.
        self.event_cart_item.early_bird_quantity = 2
        self.event_cart_item.standard_quantity = 1
        self.event_cart_item.save()
        self.cart.membership.add(self.society)
        early_bird_price = self.event.early_bird_price
        standard_price = self.event.standard_price
        ticket_price_before_discount = (
            (2 * early_bird_price) + (1 * standard_price)
        )
        membership_price = self.society.member_fee
        discount_rate = self.society.member_discount / 100
        discount_amount = discount_rate * early_bird_price
        expected_total_price = (
            ticket_price_before_discount + membership_price - discount_amount
        )
        # Test when there are no items in the cart.
        self.cart.clear()
        self.assertEqual(self.cart.total_price, Decimal('0.00'))
    
    def test_total_save(self):
        # Test when there are some items in the cart.
        price = self.event.early_bird_price
        discount = self.society.member_discount
        expected_total_save = price * discount/100
        actual_total_save = self.cart.total_saved
        self.assertEqual(expected_total_save, actual_total_save)
        # Test when there are no items in the cart.
        self.cart.clear()
        self.assertEqual(self.cart.total_saved, Decimal('0.00'))
        
    def test_count(self):
        # Test when there are some items in the cart
        # Expect count to be 2(amount of tickets) + 1(amount of society membership)
        expected_count = 3
        actual_count = self.cart.count
        self.assertEqual(expected_count, actual_count)
        # Test when there are no items in the cart
        self.cart.clear()
        self.assertEqual(self.cart.count, 0)

    def test_ticket_count(self):
        self.assertEqual(self.cart.ticket_count, 2)
        # Test ticket count updates when new event cart item added.
        new_item = EventCartItem.objects.create(
            event=self.event,
            early_bird_quantity=1,
            standard_quantity=3
        )
        self.cart.event_cart_item.add(new_item)
        self.assertEqual(self.cart.ticket_count, 6)
        # Test ticket count updates when ticket removed.
        self.event_cart_item.early_bird_quantity = 0
        self.event_cart_item.save()
        self.assertEqual(self.cart.ticket_count, 4)
    
    def test_membership_count(self):
        self.assertEqual(self.cart.membership_count, 1)
        # Test ticket count updates when new membership item added.
        new_membership = Society.objects.get(email="ai_society@kcl.ac.uk")
        self.cart.membership.add(new_membership)
        self.assertEqual(self.cart.membership_count, 2)
        # Test ticket count updates when membership removed.
        self.cart.membership.remove(self.society)
        self.assertEqual(self.cart.membership_count, 1)
    
    def test_total_ticket_price_before_discount(self):
        # Set the cart to have 2 early bird tickets and 1 standard ticket. 
        self.event_cart_item.early_bird_quantity = 2
        self.event_cart_item.standard_quantity = 1
        self.event_cart_item.save()
        early_bird_total_price = 2 * self.event.early_bird_price
        standard_total_price = 1 * self.event.standard_price
        expected_ticket_price = early_bird_total_price + standard_total_price
        actual_ticket_price = self.cart.total_ticket_price_before_discount
        self.assertEqual(actual_ticket_price, expected_ticket_price)
        
    def test_total_membership_price(self):
        # Test when there is one membership in the cart.
        expected_membership_price = self.society.member_fee
        actual_membership_price = self.cart.total_membership_price
        self.assertEqual(expected_membership_price, actual_membership_price)
        # Test total membership price updates when new membership added.
        new_membership = Society.objects.get(email="ai_society@kcl.ac.uk")
        self.cart.membership.add(new_membership)
        expected_membership_price += new_membership.member_fee
        actual_membership_price = self.cart.total_membership_price
        self.assertEqual(expected_membership_price, actual_membership_price)
        # Test total membership price updates when there is no membership added.
        self.cart.membership.clear()
        self.assertEqual(Decimal('0.00'), self.cart.total_membership_price) 
    
    def test_discount_data(self):
        # Test discount data is correct when there is early bird ticket in cart.
        self.assertTrue(self.event_cart_item.early_bird_quantity > 0)
        discount = self.event.early_bird_price * self.society.member_discount/100
        expected_discount_data = defaultdict(Decimal, {self.event_cart_item.id: discount})
        actual_discount_data = self.cart.discount_data
        self.assertEqual(expected_discount_data, actual_discount_data)
        # Test discount data is correct when there is only standard ticket.
        self.event_cart_item.early_bird_quantity = 0
        self.event_cart_item.standard_quantity = 2
        self.event_cart_item.save()
        discount = self.event.standard_price * self.society.member_discount/100
        expected_discount_data = defaultdict(Decimal, {self.event_cart_item.id: discount})
        actual_discount_data = self.cart.discount_data
        self.assertEqual(expected_discount_data, actual_discount_data)
        
    def test_get_discount_rate(self):
        # Test when there is no applicable membership for discount.
        self.cart.membership.clear()
        actual_discount_rate = self.cart.get_discount_rate(self.event_cart_item)
        self.assertEqual(actual_discount_rate, 0.0)
        # Test when there is one applicable membership for discount.
        self.society.member_discount = 10
        self.society.save()
        self.cart.membership.add(self.society)
        actual_discount_rate = self.cart.get_discount_rate(self.event_cart_item)
        self.assertEqual(actual_discount_rate, Decimal('0.1'))
        # Test the maximum discount rate applied when there are multiple 
        # applicable membership for discount.
        membership_to_add = Society.objects.get(email="ai_society@kcl.ac.uk")
        membership_to_add.member_discount = 20
        membership_to_add.save()
        self.event.society.add(membership_to_add)
        self.cart.membership.add(membership_to_add)
        actual_discount_rate = self.cart.get_discount_rate(self.event_cart_item)
        self.assertEqual(actual_discount_rate, Decimal('0.2')) 
    
    def test_membership_is_in_cart(self):
        # Test membership is in cart is correct when the membership is in cart
        self.cart.membership.add(self.society)
        membership_is_in_cart = self.cart.membership_is_in_cart(self.society)
        self.assertTrue(membership_is_in_cart)
        # Test membership is in cart updates when the membership is not in cart
        self.cart.membership.remove(self.society)
        membership_is_in_cart = self.cart.membership_is_in_cart(self.society)
        self.assertFalse(membership_is_in_cart) 
        
    def test_user_is_member(self):
        # Test when student is a member of the society.
        self.society.regular_member.add(self.student)
        user_is_member = self.cart.user_is_member(self.society)
        self.assertTrue(user_is_member)
        # Test user is member updates when the student is no longer a member
        self.society.regular_member.remove(self.student)
        user_is_member = self.cart.user_is_member(self.society)
        self.assertFalse(user_is_member) 
    
    def test_get_ticket_quantity_in_cart_per_event(self):
        # Test ticket quantity is correct when there are tickets in cart
        self.event_cart_item.early_bird_quantity = 2
        self.event_cart_item.standard_quantity = 1
        self.event_cart_item.save()
        self.cart.event_cart_item.add(self.event_cart_item) 
        early_bird_count = self.cart.get_ticket_quantity_in_cart_per_event(
            self.event, 
            'early_bird'
        )
        self.assertEqual(early_bird_count, 2) 
        standard_count = self.cart.get_ticket_quantity_in_cart_per_event(
            self.event, 
            'standard'
        ) 
        self.assertEqual(standard_count, 1) 
        # Test ticket quantity updates when there is no ticket in cart. 
        self.event_cart_item.early_bird_quantity = 0
        self.event_cart_item.standard_quantity = 0
        self.event_cart_item.save()
        early_bird_count = self.cart.get_ticket_quantity_in_cart_per_event(
            self.event, 
            'early_bird'
        )
        self.assertEqual(early_bird_count, 0) 
        standard_count = self.cart.get_ticket_quantity_in_cart_per_event(
            self.event, 
            'standard'
        ) 
        self.assertEqual(standard_count, 0)  

    def test_clear(self):
        self.assertNotEqual(len(self.cart.event_cart_item.all()), 0) 
        self.assertNotEqual(len(self.cart.membership.all()), 0) 
        # Test cart is empty after clearing the cart 
        self.cart.clear()
        self.assertEqual(len(self.cart.event_cart_item.all()), 0) 
        self.assertEqual(len(self.cart.membership.all()), 0) 