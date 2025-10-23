"""Unit tests of the checkout view"""
import json
import stripe
import os
from django.core import mail
from unittest.mock import patch, MagicMock
from tsp.json_utils.json_encoder import DecimalEncoder
from django.test import TestCase, RequestFactory
from django.contrib.messages import get_messages
from django.urls import reverse
from tsp.models import User, Student, Event, Cart, Society, EventCartItem, Order, Payment, Ticket, HistoricalCart
from tsp.forms.student.checkout_form import CheckoutForm
from tsp.views.student.checkout_view import CheckoutView
from decimal import Decimal
from stripe.error import InvalidRequestError, CardError, RateLimitError, APIConnectionError, AuthenticationError
from ticket_selling_platform import settings

class CheckoutViewTestCase(TestCase):
    """Unit tests of the checkout view"""
    
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
        # The default cart contains 2 early bird tickets of the default event
        # and the membership of the default society.
        self.cart = Cart.objects.get(student=self.student)
        self.event = Event.objects.get(pk=15)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk') 
        self.url = reverse('checkout')
        # Instantiate the view and setup with the request
        self.view = CheckoutView(student=self.student, cart=self.cart)
        factory = RequestFactory()
        self.request = factory.get(self.url)
        self.request.user = self.user
        self.view.setup(self.request)
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

    def test_request_url(self):
        self.assertEqual(self.url, '/checkout/') 
    
    def test_get_checkout_page(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/checkout.html')
    
    def test_get_checkout_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_checkout_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
        
    def test_get_context_data(self):
        context_data = self.view.get_context_data()
        self.assertIn('STRIPE_PUBLIC_KEY', context_data)
        self.assertEqual(
            context_data['STRIPE_PUBLIC_KEY'], 
            settings.STRIPE_PUBLIC_KEY
        )
        self.assertIn('email', context_data)
        self.assertEqual(context_data['email'], self.student.email)
    
    def test_get_checkout_form(self):
        form = self.view.get_form()
        self.assertIsInstance(form, CheckoutForm)
        self.assertEqual(form.initial['amount'], self.cart.total_price)
        self.assertEqual(form.initial['email'], self.student.email)
    
    def test_get_all_items_free(self):
        self.client.login(email=self.user.email, password='Password123')
        # Set all items in the cart to be free.
        self.event.early_bird_price = Decimal('0.00')
        self.event.save()
        self.society.member_fee = Decimal('0.00')
        self.society.save()
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_price, Decimal('0.00'))
        # Test that a new order is created for these free items.
        order_count_before = Order.objects.count()
        response = self.client.get(self.url)
        order_count_after = Order.objects.count()
        self.assertEqual(order_count_after, order_count_before+1)
        # Test that the response redirects to the order detail page.
        order = Order.objects.latest('pk')
        self.assertEqual(response.url, reverse('order_detail', args=[order.pk]))
        self.assertEqual(response.status_code, 302)

    def test_get_paid_items(self):
        self.client.login(email=self.user.email, password='Password123')
        self.assertNotEqual(self.cart.total_price, Decimal('0.00'))
        # Test that no order is created.
        order_count_before = Order.objects.count()
        response = self.client.get(self.url)
        order_count_after = Order.objects.count()
        self.assertEqual(order_count_after, order_count_before)
        # Test that the response redirects to the checkout page.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/checkout.html')
        
    mocked_stripe_customer = MagicMock(id='fakecus_test123')
    mocked_stripe_payment_method = MagicMock(id='pm_test123')
    @patch('stripe.Customer.create', return_value=mocked_stripe_customer)
    @patch('stripe.PaymentMethod.attach', return_value=mocked_stripe_payment_method)
    @patch('stripe.Customer.modify', return_value=mocked_stripe_customer)
    def test_successful_checkout(
        self, 
        customer_create_mock,
        payment_method_attach_mock, 
        customer_modify_mock
    ):
        self.client.login(email=self.user.email, password='Password123')
        # Set up the mock return value
        customer_create_mock.return_value = {
            'id': 'fakecus_test123',
        }
        data = self.form_input
        form = CheckoutForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Get data before checkout is completed.
        order_count_before = Order.objects.count()
        payment_before = Payment.objects.count()
        ticket_before = Ticket.objects.count()
        historical_cart_before = HistoricalCart.objects.count()
        total_price = self.cart.total_price
        total_saved = self.cart.total_saved
        count = self.cart.count
        discount_data = self.cart.discount_data
        
        # Send the request to checkout and get the order that just created.
        response = self.client.post(self.url, data=data)
        order = Order.objects.latest('pk')
        
        # Test the order is completed successfully.
        self._check_successful_order_created(order_count_before, order)
        self._check_successful_historical_cart_created(
            total_price, 
            total_saved, 
            count,
            discount_data,
            historical_cart_before,
            order
        )
        self._check_successful_payment_created(total_price, payment_before, order)
        self._check_successful_ticket_created(ticket_before)
        self._check_successful_cart_item_updated()
        self._check_successful_cart_cleared()
        self._check_successful_send_order_confirmation(order)
        
        # Test the response redirects to the order detail page
        order = Order.objects.latest('pk')
        self.assertRedirects(response, reverse('order_detail', args=[order.pk]))
    
    def _check_successful_order_created(self, order_count_before, order):       
        order_count_after = Order.objects.count()
        self.assertEqual(order_count_after, order_count_before+1)
        data = self.form_input
        self.assertEqual(order.student, self.student)
        self.assertEqual(order.line_1, data['line_1'])
        self.assertEqual(order.line_2, data['line_2'])
        self.assertEqual(order.city_town, data['city_town'])
        self.assertEqual(order.postcode, data['postcode'])
        self.assertEqual(order.country, data['country'])
    
    def _check_successful_historical_cart_created(
        self,
        total_price,
        total_saved,
        count,
        discount_data,
        historical_cart_before,
        order,
    ):        
        cart = HistoricalCart.objects.latest('pk')
        historical_cart_after = HistoricalCart.objects.count()
        self.assertEqual(historical_cart_after, historical_cart_before+1)
        self.assertEqual(cart.student, self.student)
        self.assertEqual(cart.order, order)
        self.assertEqual(cart.total_price, total_price)
        self.assertEqual(cart.total_saved, total_saved)
        self.assertEqual(cart.count, count)
        self.assertEqual(
            cart.discount_data, 
            json.dumps(discount_data, cls=DecimalEncoder)
        )
    
    def _check_successful_payment_created(self, total_price, payment_before, order):
        payment_after = Payment.objects.count()
        self.assertEqual(payment_after, payment_before+1)
        payment = Payment.objects.latest('pk')
        self.assertEqual(payment.student, self.student)
        self.assertEqual(payment.amount, total_price)
        self.assertEqual(payment.order, order)
    
    def _check_successful_ticket_created(self, ticket_before):
        ticket_after = Ticket.objects.count()
        self.assertEqual(ticket_after, ticket_before+2)
        self.assertEqual(Ticket.objects.count(), 2)
        first_ticket = Ticket.objects.all()[0]
        second_ticket = Ticket.objects.all()[1]
        self.assertEqual(first_ticket.event, self.event)
        self.assertEqual(second_ticket.event, self.event)
        self.assertEqual(first_ticket.type, 'early_bird')
        self.assertEqual(second_ticket.type, 'early_bird')
    
    def _check_successful_cart_item_updated(self):
        """
        Check if the event in the cart is marked as purchased.
        Check if the user is added to the society's members.
        Check if the event is marked as purchased with discount applied.
        """
        
        regular_members = self.society.regular_members
        purchased_events = self.student.purchased_event.all()
        discounted_events = self.student.discounted_event.all()
        self.assertIn(self.student, regular_members)
        self.assertTrue(self.event, purchased_events)
        self.assertTrue(self.event, discounted_events)
        
    def _check_successful_cart_cleared(self):
        self.assertEqual(self.cart.membership.count(), 0)
        self.assertEqual(self.cart.event_cart_item.count(), 0)
        self.assertEqual(self.cart.total_price, Decimal('0.00')) 
        self.assertEqual(self.cart.total_saved, Decimal('0.00')) 
    
    def _check_successful_send_order_confirmation(self, order):
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f'We have received your order #{order.id}')
        self.assertEqual(mail.outbox[0].to, [self.user.email])
    
    @patch('stripe.Customer.create')
    def test_handle_rate_limit_error(self, customer_create_mock):
        self.client.login(email=self.user.email, password='Password123')
        # Raise a Stripe rate limit error
        customer_create_mock.side_effect = RateLimitError(
            message='Rate Limit Error: Too many requests made. Try again later.',
            http_status=400,
        )
        data=self.form_input
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            'Rate Limit Error: Too many requests made. Try again later.'
        ) 

    @patch('stripe.Customer.create')
    def test_handle_invalid_request_error(self, customer_create_mock):
        self.client.login(email=self.user.email, password='Password123')
        # Raise a Stripe invalid request error
        customer_create_mock.side_effect = InvalidRequestError(
            message='The minimum checkout amount is GBP£0.3.',
            param=None,
            http_status=400,
        )
        data=self.form_input
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            'The minimum checkout amount is GBP£0.3.'
        ) 
    
    @patch('stripe.Customer.create')
    def test_handle_API_connection_error(self, customer_create_mock):
        self.client.login(email=self.user.email, password='Password123')
        # Raise a Stripe API connection error
        customer_create_mock.side_effect = APIConnectionError(
            message='API Connection Error: Check your network connection.',
            http_status=400,
        )
        data=self.form_input
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            'API Connection Error: Check your network connection.'
        ) 
    
    @patch('stripe.Customer.create')
    def test_handle_authentication_error(self, customer_create_mock):
        self.client.login(email=self.user.email, password='Password123')
        # Raise a Stripe API connection error
        customer_create_mock.side_effect = AuthenticationError(
            message='Authentication with Stripe API failed. Please contact support.',
            http_status=400,
        )
        data=self.form_input
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            'Authentication with Stripe API failed. Please contact support.'
        ) 
    
    @patch('stripe.Customer.create')
    def test_handle_other_stripe_errors(self, customer_create_mock):
        self.client.login(email=self.user.email, password='Password123')
        # Raise a Stripe API connection error
        customer_create_mock.side_effect = stripe.error.StripeError()
        data=self.form_input
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 
            'Something went wrong. You were not charged. Please try again.'
        ) 
    
    def test_handle_generic_error(self):
        request = self.client.get(self.url).wsgi_request
        self.view.request = request
        self.view._handle_generic_error()
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            'Generic error: Something went wrong. '\
            'You were not charged. Please try again.'
        )
    