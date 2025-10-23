"""Unit tests of the base cart form"""
from django.test import TestCase
from tsp.models import User, Society, Student, Event, Cart, EventCartItem
from tsp.forms.student.base_cart_form import BaseCartForm

class BaseEventFormTestCase(TestCase):
    """Unit tests of the base cart form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/other_events.json',
        'tsp/tests/fixtures/default_cart.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.student = self.user.student
        self.event = Event.objects.get(pk=15)
        self.cart = Cart.objects.get(student=self.student)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.form_input = {
            'early_bird_to_add': 2,
            'standard_to_add': 0,
            'membership': '',
        }   

    def test_valid_form(self):
        form = BaseCartForm(data=self.form_input, user=self.user, event=self.event)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = BaseCartForm(user=self.user, event=self.event)
        self.assertIn('early_bird_to_add', form.fields)
        self.assertIn('standard_to_add', form.fields)
        self.assertIn('membership', form.fields)

    def test_save(self):
        event_cart_items = self.cart.event_cart_item.all()
        self.assertIn(self.event_cart_item, event_cart_items)
        self.assertEqual(event_cart_items.count(), 1)
        self.assertEqual(event_cart_items.first(), self.event_cart_item)
        early_bird_ticket_in_cart_before = self.event_cart_item.early_bird_quantity
        standard_ticket_in_cart_before = self.event_cart_item.standard_quantity
        form = BaseCartForm(data=self.form_input, user=self.user, event=self.event)
        self.assertTrue(form.is_valid())
        cart = form.save()
        # Test the cart saves correctly after the form submitted
        early_bird_to_add = form.cleaned_data['early_bird_to_add']
        standard_to_add = form.cleaned_data['standard_to_add']
        early_bird_ticket_in_cart_after = early_bird_ticket_in_cart_before + early_bird_to_add
        standard_ticket_in_cart_after = standard_ticket_in_cart_before + standard_to_add
        self.assertEqual(event_cart_items.count(), 1)
        self.assertEqual(
            event_cart_items.first().early_bird_quantity, 
            early_bird_ticket_in_cart_after
        )
        self.assertEqual(
            cart.event_cart_item.all()[0].standard_quantity, 
            standard_ticket_in_cart_after
        )
        self.assertEqual(cart.membership.count(), 1)
        self.assertTrue(form.is_valid())
    
    def test_update_event_cart_item(self):
        early_bird_ticket_count_before = self.event_cart_item.early_bird_quantity
        standard_ticket_count_before = self.event_cart_item.standard_quantity
        form = BaseCartForm(user=self.user, event=self.event)
        form.update_event_cart_item(2, 3)
        self.event_cart_item.refresh_from_db()
        early_bird_ticket_count_after = self.event_cart_item.early_bird_quantity
        standard_ticket_count_after = self.event_cart_item.standard_quantity
        self.assertEqual(
            early_bird_ticket_count_before + 2, 
            early_bird_ticket_count_after
        )
        self.assertEqual(
            standard_ticket_count_before + 3, 
            standard_ticket_count_after
        )

    def test_update_cart_by_updating_event_cart_item(self):
        event_cart_items = self.cart.event_cart_item.all()
        self.assertIn(self.event_cart_item, event_cart_items)
        self.event_cart_item.early_bird_quantity = 4
        self.event_cart_item.standard_quantity = 2
        self.event_cart_item.save()
        form = BaseCartForm(user=self.user, event=self.event)
        form.update_cart(None)
        # Test the cart updates correctly when updating an existing event cart item.
        updated_event_cart_items = self.cart.event_cart_item.all()
        update_event_cart_item = updated_event_cart_items.get(pk=self.event_cart_item.pk)
        self.assertEqual(update_event_cart_item.event, self.event_cart_item.event)
        self.assertEqual(update_event_cart_item.early_bird_quantity, 4)
        self.assertEqual(update_event_cart_item.standard_quantity, 2)
        
    def test_get_available_ticket_quantity_when_no_ticket_available(self):
        self.event.early_booking_capacity = 0
        self.event.standard_booking_capacity = 0
        self.event.save()
        form = BaseCartForm(data=self.form_input, user=self.cart, event=self.event)
        self.assertEqual(form._get_available_ticket_quantities('early_bird'), 0)
        self.assertEqual(form._get_available_ticket_quantities('standard'), 0)
        
    def test_get_available_ticket_quantity_when_cart_is_empty(self):
        # Test the ticket quantity for an empty cart is the same as ticket inventory.
        self.cart.clear()
        form = BaseCartForm(data=self.form_input, user=self.cart, event=self.event)
        early_bird_inventory = Event.get_event_ticket_inventory(self.event, 'early_bird')
        standard_inventory = Event.get_event_ticket_inventory(self.event, 'standard')
        early_bird_availability = form._get_available_ticket_quantities('early_bird')
        standard_availability = form._get_available_ticket_quantities('standard')
        self.assertEqual(early_bird_inventory, early_bird_availability)
        self.assertEqual(standard_inventory, standard_availability)

    def test_get_available_ticket_quantity_when_tickets_added_into_cart(self):
        # Test ticket quantity is updated based on the number of tickets in cart.
        form = BaseCartForm(data=self.form_input, user=self.cart, event=self.event)
        early_bird_ticket_in_cart = self.event_cart_item.early_bird_quantity
        standard_ticket_in_cart = self.event_cart_item.standard_quantity
        early_bird_inventory = Event.get_event_ticket_inventory(self.event, 'early_bird')
        standard_inventory = Event.get_event_ticket_inventory(self.event, 'standard')
        early_bird_availability = early_bird_inventory - early_bird_ticket_in_cart
        standard_availability = standard_inventory - standard_ticket_in_cart
        self.assertEqual(form._get_available_ticket_quantities('early_bird'), early_bird_availability)
        self.assertEqual(form._get_available_ticket_quantities('standard'), standard_availability)
        
        # Test the ticket quantity updates correctly after adding more tickets to cart.
        self.assertTrue(form.is_valid())
        cart = form.save()
        early_bird_to_add = form.cleaned_data['early_bird_to_add']
        standard_to_add = form.cleaned_data['standard_to_add']
        early_bird_availability = early_bird_availability - early_bird_to_add
        standard_availability = standard_availability - standard_to_add
        self.assertEqual(form._get_available_ticket_quantities('early_bird'), early_bird_availability)
        self.assertEqual(form._get_available_ticket_quantities('standard'), standard_availability)
        
    def test_initialization_sets_user_and_event(self):
        form = BaseCartForm(user=self.user, event=self.event)
        self.assertEqual(form.user, self.user)
        self.assertEqual(form.event, self.event)
    
    def test_initialization_creates_cart_and_event_cart_item(self):
        form = BaseCartForm(user=self.user, event=self.event)
        self.assertIsNotNone(form.cart)
        self.assertIsNotNone(form.event_cart_item)

    def test_initialization_does_not_create_cart_or_event_cart_item_when_user_is_none(self):
        form = BaseCartForm(user=None, event=self.event)
        self.assertIsNone(form.cart)
        self.assertIsNone(form.event_cart_item) 
    
    def test_initialization_does_not_create_event_cart_item_when_event_is_none(self):
        form = BaseCartForm(user=self.user, event=None)
        self.assertIsNone(form.event_cart_item) 
    
    def test_initialization_does_not_create_event_cart_item_when_cart_is_none(self):
        self.user.cart = None
        form = BaseCartForm(data=self.form_input, user=self.user)
        self.assertIsNone(form.event_cart_item)
   
    
