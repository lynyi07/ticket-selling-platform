"""Unit tests of the add to cart view"""
from django.test import TestCase
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from django.contrib.messages import get_messages
from django.contrib.messages import constants as message_constants
from tsp.models import User, Student, Event, Cart, Society, EventCartItem
from tsp.forms.student.add_to_cart_form import AddToCartForm
from tsp.views.student.add_to_cart_view import AddToCartView

class AddToCartViewTestCase(TestCase):
    """Unit tests of the add to cart view"""
    
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
        # The default cart contains 2 early bird tickets of the default event 
        # and the membership of the default society membership
        self.cart = Cart.objects.get(student=self.user)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.default_society = Society.objects.get(email='tech_society@kcl.ac.uk')
        # Set another society to organise the given event together with the 
        # default society
        self.other_society = Society.objects.get(email='ai_society@kcl.ac.uk')
        self.event.society.add(self.other_society)
        self.form_input = {
            'early_bird_to_add': 2,
            'standard_to_add': '',
            'membership': self.other_society.id,
            'event_pk': self.event.pk
        }      
        self.url = reverse('add_to_cart')        
        
    def test_request_url(self):
        self.assertEqual(self.url, '/add_to_cart/')
        
    def test_post_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, {'event_pk': self.event.pk}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/add_to_cart.html')
        self.assertIsInstance(response.context['form'], AddToCartForm)
    
    def test_get_request_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_request_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_request_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
        
    def test_successful_create_and_add_event_cart_item(self):
        self.cart.clear()
        self.client.login(email=self.user.email, password='Password123')
        event_cart_item_count_before = EventCartItem.objects.count()
        event_cart_item_in_cart_before = self.cart.event_cart_item.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.cart.refresh_from_db()
        event_cart_item_count_after = EventCartItem.objects.count()
        event_cart_item_in_cart_after = self.cart.event_cart_item.count()
        # Test a new event cart item object is created and added to cart.
        self.assertEqual(event_cart_item_in_cart_after, event_cart_item_in_cart_before+1)
        self.assertEqual(event_cart_item_count_after, event_cart_item_count_before+1)
        response_url = reverse('event_page', args=[self.event.id])
        self.assertTemplateUsed(response, 'student/event_page.html')
        event_cart_item = self.cart.event_cart_item.get(event=self.event)
        self.assertEqual(event_cart_item.early_bird_quantity, 2)
        self.assertEqual(event_cart_item.standard_quantity, 0)
        # Test the success message is correct.
        expected_message = "Added to basket."
        self._test_message(expected_message, response)
    
    def test_successful_update_event_cart_item(self):        
        self.client.login(email=self.user.email, password='Password123')
        # Test the event cart item is already in cart.
        event_cart_item = self.cart.event_cart_item.get(event=self.event)
        event_cart_items = self.cart.event_cart_item.all()
        self.assertIn(event_cart_item, event_cart_items)
        # Test that no new event cart item object is created for the given event.
        event_cart_item_count_before = EventCartItem.objects.count()
        event_cart_item_in_cart_before = self.cart.event_cart_item.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.cart.refresh_from_db()
        event_cart_item_count_after = EventCartItem.objects.count()
        event_cart_item_in_cart_after = self.cart.event_cart_item.count()
        self.assertEqual(event_cart_item_in_cart_after, event_cart_item_in_cart_before)
        self.assertEqual(event_cart_item_count_after, event_cart_item_count_before)
        response_url = reverse('event_page', args=[self.event.id])
        self.assertTemplateUsed(response, 'student/event_page.html')
        # Test the existing event cart item attributes update correctly
        early_bird_quantity_before = event_cart_item.early_bird_quantity
        standard_quantity_before = event_cart_item.standard_quantity
        event_cart_item.refresh_from_db()
        early_bird_quantity_after = early_bird_quantity_before + 2
        standard_quantity_after = standard_quantity_before + 0
        expected_early_bird_quantity = event_cart_item.early_bird_quantity
        expected_standard_quantity = event_cart_item.standard_quantity
        self.assertEqual(expected_early_bird_quantity, early_bird_quantity_after)
        self.assertEqual(expected_standard_quantity, standard_quantity_after)
        # Test the success message is correct
        expected_message = "Added to basket."
        self._test_message(expected_message, response)
        
    def test_successful_add_membership_to_cart(self): 
        self.client.login(email=self.user.email, password='Password123')
        memberships = self.cart.membership.all()
        membership_count_before = memberships.count()
        self.assertNotIn(self.other_society, memberships)
        # Test the cart updates correctly after adding the membership to it.
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.cart.refresh_from_db()
        memberships = self.cart.membership.all()
        membership_count_after = memberships.count()
        self.assertIn(self.other_society, memberships)
        self.assertEqual(membership_count_after, membership_count_before+1)
        # Test the success message is correct
        expected_message = "Added to basket."
        self._test_message(expected_message, response)
    
    def test_can_not_add_membership_if_it_is_already_in_cart(self): 
        # Test the membership is already in cart.
        self.client.login(email=self.user.email, password='Password123')
        memberships = self.cart.membership.all()
        membership_count_before = self.cart.membership.count()
        self.assertIn(self.default_society, memberships)
        # Test user can not add the same memebership to cart again.
        self.form_input['membership'] = self.default_society
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.cart.refresh_from_db()
        self.assertFalse(response.context['form'].is_valid())
        membership_count_after = self.cart.membership.count()
        self.assertEqual(membership_count_before, membership_count_after)
        # Test the error message is correct.
        expected_message = "Something went wrong..."
        self._test_message(expected_message, response)
        
    def test_can_not_add_membership_if_user_is_already_a_member(self): 
        # Set user as a regular member of the given society.
        self.default_society.add_regular_member(self.user)
        self.assertIn(self.user, self.default_society.regular_members)
        # Test user can not add the given society membership to cart.
        self.client.login(email=self.user.email, password='Password123')
        membership_count_before = self.cart.membership.count()
        self.form_input['membership'] = self.default_society
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.cart.refresh_from_db()
        self.assertFalse(response.context['form'].is_valid())
        membership_count_after = self.cart.membership.count()
        self.assertEqual(membership_count_before, membership_count_after)
        # Test the error message is correct.
        expected_message = "Something went wrong..."
        self._test_message(expected_message, response)

    def _test_message(self, expected_message, response):
        messages = list(response.context['messages'])
        self.assertTrue(len(messages), 1) 
        actual_message = messages[0].message
        self.assertIn(expected_message, actual_message) 