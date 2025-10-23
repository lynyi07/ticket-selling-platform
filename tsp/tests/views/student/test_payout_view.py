"""Unit tests of the payout view"""
import stripe
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.urls import reverse
from tsp.models import User, Student, Event, Cart, Society, EventCartItem, Order
from tsp.views.student.payout_view import PayoutView

class PayoutViewTestCase(TestCase): 
    """Unit tests of the payout view"""
    
    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/other_events.json',
        'tsp/tests/fixtures/default_cart.json',
        'tsp/tests/fixtures/default_order.json'
    ]
    
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.student = self.user.student
        self.cart = Cart.objects.get(student=self.student)
        self.event = Event.objects.get(pk=15)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk') 
        self.other_event = Event.objects.get(pk=27)
        self.other_society = Society.objects.get(email='robotics@qmw.ac.uk')
        self.other_event_cart_item = EventCartItem.objects.create(
            event = self.other_event,
            early_bird_quantity=10,
            standard_quantity=0
        )
        self.other_user = Student.objects.get(email='janedoe@kcl.ac.uk')
        self.view = PayoutView()
        self.factory = RequestFactory()
        self.form_input = {
            'payment_method_id': 'pm_test',
            'full_name': self.student.full_name,
            'email': self.student.email,
            'line_1': 'Strand',
            'line_2': "King's College London",
            'city_town': 'London',
            'postcode': 'WC2R 2LS',
            'country': 'United Kingdom',
            'amount': ''
        }   
        
    def test_get_order_items(self):
        self.client.login(email=self.other_user.email, password='Password123')
        cart = Cart.objects.create(student = self.other_user)
        cart.event_cart_item.add(self.event_cart_item)
        cart.membership.add(self.society)
        items = self.view._get_order_items(cart)
        # Check the cart contains 2 items, one event cart item and one society 
        # membership.assert
        self.assertEqual(len(items), 2)
        self.assertIn(self.event_cart_item, items)
        self.assertIn(self.society, items)
        
    def test_get_order_by_seller(self):
        order_items = [
            self.event_cart_item, 
            self.other_event_cart_item, 
            self.society, 
            self.other_society
        ]
        items = self.view._get_order_items_by_seller(order_items)
        self.assertIn(self.society, items)
        self.assertIn(self.other_society, items)
        self.assertIn(self.event_cart_item,  items[self.society])
        self.assertIn(self.other_event_cart_item, items[self.other_society])

    def test_calculate_payouts(self):
        self.cart.membership.add(self.other_society)
        self.cart.event_cart_item.add(self.other_event_cart_item)
        seller_items = {
            self.society: [self.event_cart_item, self.society],
            self.other_society: [self.other_event_cart_item, self.other_society]
        }
        payouts = self.view._get_payouts(seller_items, self.cart)
        self.assertIn(self.society, payouts)
        self.assertIn(self.other_society, payouts)
        # Calculate the total amount of ticket price and membership fee.
        expected_payout_society_first = (
            self.society.member_fee + 
            (self.event_cart_item.early_bird_quantity * self.event.early_bird_price) + 
            (self.event_cart_item.standard_quantity * self.event.standard_price)
        )
        expected_payout_society_second = (
            self.other_society.member_fee + 
            (self.other_event_cart_item.early_bird_quantity * self.other_event.early_bird_price) + 
            (self.other_event_cart_item.standard_quantity * self.other_event.standard_price)
        )
        # Deduct discount if applicable 
        discount_data = self.cart.discount_data
        discount_applied_first = discount_data.get(self.event_cart_item.id, 0)
        discount_applied_second = discount_data.get(self.other_event_cart_item.id, 0)
        expected_payout_society_first -= discount_applied_first
        expected_payout_society_second -= discount_applied_second
        self.assertEqual(payouts[self.society], expected_payout_society_first)
        self.assertEqual(payouts[self.other_society], expected_payout_society_second)
    
    @patch('stripe.Customer.create', return_value=MagicMock(id='fakecus_test123'))
    @patch('stripe.PaymentMethod.attach', return_value=MagicMock(id='pm_test123'))
    @patch('stripe.Customer.modify', return_value=MagicMock(id='fakecus_test123'))
    @patch('stripe.Customer.retrieve')
    @patch('stripe.PaymentMethod.retrieve')
    @patch('stripe.PaymentIntent.create')
    def test_initiate_payout(
        self, 
        payment_intent_create_mock, 
        payment_method_retrieve_mock, 
        customer_retrieve_mock, 
        customer_modify_mock, 
        mock_payment_method_attach, 
        mock_customer_create
    ):
        self.client.login(email=self.user.email, password='Password123')
        # Set up the mock return values
        customer_retrieve_mock.return_value = MagicMock(
            invoice_settings=MagicMock(default_payment_method='pm_test123')
        )
        payment_method_retrieve_mock.return_value = MagicMock()
        payment_intent_create_mock.return_value = MagicMock(confirm=MagicMock())
        # Checkout and get the latest order.
        data = self.form_input
        response = self.client.post(reverse('checkout'), data=data)
        order = Order.objects.get(pk=29)
        payouts = {
            self.society: 10,
            self.other_society: 20
        }
        self.view._initiate_payout(order, payouts)
        # Check if the Stripe API calls are being made with the correct parameters
        customer_retrieve_mock.assert_called_with(order.customer_id)
        payment_method_retrieve_mock.assert_called_with('pm_test123')
        for seller, payout_amount in payouts.items():
            payment_intent_create_mock.assert_any_call(
                amount=int(payout_amount * 100),
                currency='gbp',
                payment_method='pm_test123',
                customer=order.customer_id,
                payment_method_types=['card'],
                transfer_data={
                    'destination': seller.stripe_account_id
                },
            )
            payment_intent_create_mock.return_value.confirm.assert_called()
        # Test the correct amount of payment intents have been created.
        self.assertEqual(len(payouts), len(payment_intent_create_mock.call_args_list))
