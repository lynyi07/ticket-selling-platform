"""Unit tests of the Payment model"""
from django.test import TestCase
from decimal import Decimal
from tsp.models import Payment, Order, Student, HistoricalCart

class PaymentModelTestCase(TestCase):
    """Unit tests of the Payment model"""
    
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
        self.historical_cart = HistoricalCart.objects.get(order=self.order)
        self.payment = Payment.objects.get(order=self.order)
    
    def test_student(self):
        expected_student = self.student
        actual_student = self.payment.student
        self.assertEquals(expected_student, actual_student)
    
    def test_order(self):
        expected_order = self.order
        actual_order = self.payment.order
        self.assertEquals(expected_order, actual_order)
    
    def test_amount(self):
        expected_amount = self.historical_cart.total_price 
        actual_amount = self.payment.amount 
        self.assertEquals(expected_amount, actual_amount) 
    
    def test_status_choices(self):
        choices = self.payment._meta.get_field('status').choices
        self.assertEqual(choices, Payment.Status.choices)
         
    def test_default_status(self):
        default_status = Payment._meta.get_field('status').default
        self.assertEqual(default_status, Payment.Status.COMPLETED) 

    def test_last4(self):
        # Test last 4 are all digits
        actual_last4 = self.payment.last4 
        self.assertTrue(actual_last4.isdigit())
        
    def test_brand(self):
        # Test accepted brand is used
        expected_brands = ['visa', 'amex', 'mastercard', 'unionpay']
        actual_brand = self.payment.brand
        self.assertIn(actual_brand, expected_brands) 
    
    