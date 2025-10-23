"""Unit tests of the BaseCart model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from tsp.models import EventCartItem, BaseCart, Society

class DomainModelTestCase(TestCase):
    """Unit tests of the BaseCart model"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]

    def setUp(self):
        self.cart = BaseCart.objects.get(pk=26)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')
        
    def test_event_cart_item(self):
        self.cart.event_cart_item.add(self.event_cart_item)
        event_cart_items = self.cart.event_cart_item.all()
        self.assertIn(self.event_cart_item, event_cart_items)

    def test_membership(self):
        self.cart.membership.add(self.society)
        memberships = self.cart.membership.all()
        self.assertIn(self.society, memberships)