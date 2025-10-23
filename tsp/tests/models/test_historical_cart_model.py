"""Unit tests of the HistoricalCart model"""
from django.test import TestCase
from tsp.models import Student, HistoricalCart, Order, Cart
from collections import defaultdict

class HistoricalCartModelTestCase(TestCase):
    """Unit tests of the HistoricalCart model"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json',
        'tsp/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        # Cart of the current student
        self.cart = Cart.objects.get(pk=26) 
        
    def test_student(self):
        expected_student = self.student
        historical_cart = self._get_historical_cart()
        actual_student = historical_cart.student
        self.assertEqual(actual_student, expected_student)
        
    def test_total_price(self):
        expected_total_price = self.cart.total_price
        historical_cart = self._get_historical_cart()
        actual_total_price = historical_cart.total_price
        self.assertEqual(actual_total_price, expected_total_price) 
    
    def test_total_saved(self):
        expected_total_saved = self.cart.total_saved
        historical_cart = self._get_historical_cart()
        actual_total_saved = historical_cart.total_saved
        self.assertEqual(expected_total_saved, actual_total_saved) 
    
    def test_count(self):
        expected_count = self.cart.count
        historical_cart = self._get_historical_cart()
        actual_count = historical_cart.count
        self.assertEqual(expected_count, actual_count) 
    
    def test_discount_data(self):
        expected_discount_data = self.cart.discount_data 
        historical_cart = self._get_historical_cart()
        actual_discount_data = historical_cart.discount_data_dict 
        self.assertEqual(expected_discount_data, actual_discount_data)
    
    def _get_historical_cart(self):
        order = self._create_order()
        historical_cart = HistoricalCart.objects.get(order=order)
        return historical_cart
    
    def _create_order(self):
        cart = Order.objects.create(
            student=self.student,
            customer_id="fakecus_12345",
            line_1="Strand",
            line_2="King's College London",
            city_town="London",
            postcode="WC2R 2LS",
            country="United Kingdom"
        )
        return cart