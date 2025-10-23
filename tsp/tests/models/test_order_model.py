"""Unit tests of the Order model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from tsp.models import Student, HistoricalCart, Order, Cart
from django.utils import timezone
import datetime

class OrderModelTestCase(TestCase):
    """Unit tests of the Order model"""

    fixtures = [
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json',
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_order.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.order = Order.objects.get(pk=29)
    
    def test_student(self):
        expected_student = self.student
        actual_student = self.order.student
        self.assertEquals(expected_student, actual_student)
        
    def test_customer_id(self):
        expected_customer_id = "fakecus_customer_id"
        actual_customer_id = self.order.customer_id
        self.assertEquals(expected_customer_id, actual_customer_id)
        
    def test_create_at_defaults_to_now(self):
        expected_create_at = timezone.now()
        actual_create_at = self.order.create_at
        # There may be a slight delay between when the expected create_at time 
        # is set and when the actual create_at time is set due to the time 
        # it takes to create the order object in the database.
        self.assertLessEqual(
            actual_create_at - expected_create_at,
            datetime.timedelta(seconds=1),
        )
    
    def test_line_1(self):
        expected_line_1 = "Strand"
        actual_line_1 = self.order.line_1
        self.assertEquals(expected_line_1, actual_line_1) 
    
    def test_line_1_must_not_be_empty(self):
        self.order.line_1 = None
        with self.assertRaises(ValidationError):
            self.order.full_clean()
    
    def test_line_2(self):
        expected_line_2 = "King's College London"
        actual_line_2 = self.order.line_2
        self.assertEquals(expected_line_2, actual_line_2)
    
    def test_city_town(self):
        expected_city_town = "London"
        actual_city_town = self.order.city_town
        self.assertEquals(expected_city_town, actual_city_town)
    
    def test_city_town_must_not_be_empty(self):
        self.order.city_town = None
        with self.assertRaises(ValidationError):
            self.order.full_clean() 
        
    def test_postcode(self):
        expected_postcode = "WC2R 2LS"
        actual_postcode = self.order.postcode
        self.assertEquals(expected_postcode, actual_postcode)
    
    def test_postcode_must_not_be_empty(self):
        self.order.postcode = None
        with self.assertRaises(ValidationError):
            self.order.full_clean()
       
    def test_country(self):
        expected_country = "United Kingdom"
        actual_country = self.order.country
        self.assertEquals(expected_country, actual_country)
    
    def test_country_must_not_be_empty(self):
        self.order.country = None
        with self.assertRaises(ValidationError):
            self.order.full_clean()
       
    def test_get_orders_by_student(self):
        expected_orders = [self.order]
        actual_orders = Order.get_orders_by_student(self.student)
        self.assertEqual(list(expected_orders), list(actual_orders))
        
    def test_meta_ordering(self):
        expected_ordering = ['-create_at']
        actual_ordering = Order._meta.ordering
        self.assertEqual(expected_ordering, actual_ordering)

        