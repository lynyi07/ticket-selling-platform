"""Unit tests of the cart detail view"""
from django.test import TestCase
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from django.contrib.messages import get_messages
from django.contrib.messages import constants as message_constants
from tsp.models import User, Student, Event, Cart, Society, EventCartItem
from tsp.views.student.cart_detail_view import CartDetailView
from decimal import Decimal

class CartDetailViewTestCase(TestCase):
    """Unit tests of the cart detail view"""
    
    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json'
    ]
    
    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.event = Event.objects.get(pk=15)
        # The default cart contains 2 early bird tickets of the default
        # event and the default society's membership.
        self.cart = Cart.objects.get(student=self.user)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.view = CartDetailView()
        self.url = reverse('cart_detail')       
    
    def test_url(self):
        self.assertEqual(self.url, '/cart_detail/') 
    
    def test_get_cart_detail_page(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/cart_detail.html')
    
    def test_get_cart_detail_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_cart_detail_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_object(self):        
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/cart_detail.html')
        # Check if the cart is correctly created or retrieved
        cart = Cart.objects.get(student=self.user)
        self.assertIsNotNone(cart)
        self.assertEqual(response.context['cart'], cart) 
    
    def test_get_context_data(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/cart_detail.html')
        context = response.context
        event_cart_items = context['event_cart_items']
        memberships = context['memberships']
        self.assertIn(self.event_cart_item, event_cart_items)
        self.assertIn(self.society, memberships)
        self.assertEqual(context['total_saved'], self.cart.total_saved)
        self.assertEqual(context['total_price'], self.cart.total_price)
        self.assertEqual(context['count'], self.cart.count)
        
    def test_successful_discount_applied_with_membership_in_cart(self):
        members = self.society.regular_members
        self.assertNotIn(self.user, members)
        memberships_in_cart = self.cart.membership.all()
        self.assertIn(self.society, memberships_in_cart)
        discounted_events = self.user.discounted_event.all()
        self.assertNotIn(self.event, discounted_events)
        discount_rate = self.society.member_discount
        expected_discount = self.event_cart_item.get_discount_amount(discount_rate)
        actual_discount = self.cart.total_saved
        self.assertEqual(expected_discount, 100 * actual_discount)
    
    def test_successful_discount_applied_when_user_is_a_member(self):
        self.society.add_regular_member(self.user)
        members = self.society.regular_members
        self.assertIn(self.user, members)
        self.cart.membership.remove(self.society)
        memberships_in_cart = self.cart.membership.all()
        self.assertNotIn(self.society, memberships_in_cart)
        discounted_events = self.user.discounted_event.all()
        self.assertNotIn(self.event, discounted_events)
        discount_rate = self.society.member_discount
        expected_discount = self.event_cart_item.get_discount_amount(discount_rate)
        actual_discount = self.cart.total_saved
        self.assertEqual(expected_discount, 100 * actual_discount)
    
    def test_discount_not_applied_when_no_associated_membership_found(self):
        self.society.regular_member.remove(self.user)
        self.cart.membership.remove(self.society)
        discounted_events = self.user.discounted_event.all()
        self.assertNotIn(self.event, discounted_events)
        expected_discount = Decimal('0.00')
        actual_discount = self.cart.total_saved
        self.assertEqual(expected_discount, 100 * actual_discount)
    
    def test_successful_discount_applied_when_user_already_purchased_without_discount(self):
        self.user.purchase_event(self.event)
        # Test the discount is applied when membership is in cart and user has 
        # not purchased the event ticket with discount.
        memberships_in_cart = self.cart.membership.all()
        self.assertIn(self.society, memberships_in_cart)
        discounted_events = self.user.discounted_event.all()
        self.assertNotIn(self.event, discounted_events)
        discount_rate = self.society.member_discount
        expected_discount = self.event_cart_item.get_discount_amount(discount_rate)
        actual_discount = self.cart.total_saved
        self.assertEqual(expected_discount, 100 * actual_discount)
    
    def test_discount_not_applied_when_user_already_purchased_with_discount(self):
        self.user.purchase_discounted_event(self.event)
        # Test discount is not applied when user already purchased the event
        # ticket with discount applied.
        expected_discount = Decimal('0.00')
        actual_discount = self.cart.total_saved
        self.assertEqual(expected_discount, 100 * actual_discount)