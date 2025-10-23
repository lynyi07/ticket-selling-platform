"""Unit tests of the add to cart view"""
import json
from django.http import HttpRequest
from django.test import TestCase, RequestFactory
from django.urls import reverse
from tsp.tests.helpers import reverse_with_next
from tsp.models import User, Student, Event, Cart, Society, EventCartItem
from tsp.forms.student.update_cart_form import UpdateCartForm
from tsp.views.student.update_cart_view import UpdateCartView

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
        self.user = User.objects.get(pk=1)
        self.student = self.user.student
        self.event = Event.objects.get(pk=15)
        self.cart = Cart.objects.get(student=self.student)
        self.event_cart_item = EventCartItem.objects.get(pk=25)
        self.society = Society.objects.get(email='tech_society@kcl.ac.uk') 
        self.factory = RequestFactory()
        self.url = reverse('update_cart')       
        self.view = UpdateCartView()
        
    def test_get_object(self):
        request = self.factory.get(self.url)
        request.user = self.user
        self.view.request = request
        cart = self.view.get_object()
        self.assertEqual(cart, self.cart)
        
    def test_request_url(self):
        self.assertEqual(self.url, '/update_cart/')
        
    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('cart_detail')) 
        self.assertTemplateUsed(response, 'student/cart_detail.html')
    
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
        
    def test_ajax_request_max_availability(self):
        self.client.login(email=self.user.email, password='Password123')
        # Create the data dictionary for the request
        request_data = {
            'event_cart_item_id': self.event_cart_item.id,
            'action': 'get_max_availability'
        }
        # Send an AJAX request
        response = self.client.get(
            self.url,
            request_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        # Test the JsonResponse content is correct
        response_data = json.loads(response.content)
        self.assertIn('early_bird_availability', response_data)
        self.assertIn('standard_availability', response_data)

    def test_increase_number_of_tickets(self):
        self.client.login(email=self.user.email, password='Password123')
        request_data = {
            'event_cart_item_id': self.event_cart_item.id,
            'early_bird_to_add': 2
        }
        early_bird_quantity_before = self.event_cart_item.early_bird_quantity
        response = self.client.post(self.url, request_data)
        # Test if the response is a JSON response with success status.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Test if the event cart item updates correctly.
        updated_event_cart_item = EventCartItem.objects.get(id=self.event_cart_item.id)
        actual_early_bird_quantity = updated_event_cart_item.early_bird_quantity
        expected_early_bird_quantity = early_bird_quantity_before + 2
        self.assertEqual(actual_early_bird_quantity, expected_early_bird_quantity)

    def test_decrease_number_of_tickets(self):
        self.client.login(email=self.user.email, password='Password123')
        request_data = {
            'event_cart_item_id': self.event_cart_item.id,
            'early_bird_to_add': -1
        }
        early_bird_quantity_before = self.event_cart_item.early_bird_quantity
        response = self.client.post(self.url, request_data)
        # Test if the response is a JSON response with success status.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Test if the event cart item updates correctly.
        updated_event_cart_item = EventCartItem.objects.get(id=self.event_cart_item.id)
        actual_early_bird_quantity = updated_event_cart_item.early_bird_quantity
        expected_early_bird_quantity = early_bird_quantity_before - 1
        self.assertEqual(actual_early_bird_quantity, expected_early_bird_quantity)
    
    def test_event_cart_item_removed_when_number_of_tickets_is_zero(self):
        self.client.login(email=self.user.email, password='Password123')
        event_cart_items = self.cart.event_cart_item.all()
        self.assertIn(self.event_cart_item, event_cart_items)
        event_cart_item_in_cart_before = event_cart_items.count()
        early_bird_quantity_before = self.event_cart_item.early_bird_quantity
        standard_quantity_before = self.event_cart_item.standard_quantity
        request_data = {
            'event_cart_item_id': self.event_cart_item.id,
            'early_bird_to_add': -early_bird_quantity_before,
            'standard_to_add': -standard_quantity_before
        }
        response = self.client.post(self.url, request_data)
        # Test if the response is a JSON response with success status.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Test if the event cart item is removed from the cart.
        self.cart.refresh_from_db()
        event_cart_items = self.cart.event_cart_item.all()
        self.assertNotIn(self.event_cart_item, event_cart_items)
        actual_event_cart_item_count = event_cart_items.count()
        expected_event_cart_item_count = event_cart_item_in_cart_before - 1
        self.assertEqual(expected_event_cart_item_count, actual_event_cart_item_count)
    
    def test_remove_membership(self):
        self.client.login(email=self.user.email, password='Password123')
        memberships = self.cart.membership.all()
        memberships_in_cart_before = memberships.count()
        self.assertIn(self.society, memberships)
        request_data = {
            'membership_to_remove_id': self.society.id
        }
        response = self.client.post(self.url, request_data)
        # Test if the response is a JSON response with success status.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        # Test if the specified membership is removed from the cart.
        self.cart.refresh_from_db()
        memberships = self.cart.membership.all()
        self.assertNotIn(self.society, memberships)
        actual_membership_count = memberships.count()
        expected_membership_count = memberships_in_cart_before - 1
        self.assertEqual(expected_membership_count, actual_membership_count)
        
    def test_get_valid_event_cart_item(self):
        request = HttpRequest()
        request.POST['event_cart_item_id'] = self.event_cart_item.id
        result = self.view._get_event_cart_item(self.cart, request)
        self.assertEqual(result, self.event_cart_item)
    
    def test_get_invalid_event_cart_item(self):
        request = HttpRequest()
        request.POST['event_cart_item_id'] = -1
        result = self.view._get_event_cart_item(self.cart, request)
        self.assertIsNone(result)
    
    def test_get_valid_membership_to_remove(self):
        request = HttpRequest()
        request.POST['membership_to_remove_id'] = self.society.id
        result = self.view._get_membership_to_remove(request)
        self.assertEqual(result, self.society)
    
    def test_get_invalid_membership_to_remove(self):
        request = HttpRequest()
        request.POST['membership_to_remove_id'] = -1
        result = self.view._get_membership_to_remove(request)
        self.assertIsNone(result)
        
    def test_handle_form_data(self):
        request = HttpRequest()
        request.user = self.user
        request.POST['event_cart_item_id'] = self.event_cart_item.id
        request.POST['membership_to_remove_id'] = self.society.id
        result = self.view._handle_form_data(request, self.society, self.cart)
        # Test if the result is an instance of UpdateCartForm and if the form
        # data is correct.
        self.assertIsInstance(result, UpdateCartForm)
        self.assertEqual(result.data['membership'], self.society)
        self.assertEqual(result.instance, self.cart)
        self.assertEqual(result.initial['membership'][0], self.society)
        self.assertEqual(result.instance.student, self.student)
