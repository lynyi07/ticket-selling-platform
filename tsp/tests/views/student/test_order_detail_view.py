"""Unit tests of the order detail view"""
from django.test import TestCase
from django.urls import reverse
from django.test import RequestFactory
from tsp.models import User, Society, Event, Student, Cart, Order, EventCartItem, Payment
from tsp.views.student.order_detail_view import OrderDetailView

class OrderDetailViewTestCase(TestCase):
    """Unit tests of the order detail view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json',
        'tsp/tests/fixtures/default_cart.json',
        'tsp/tests/fixtures/default_order.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.student = self.user.student
        self.cart = Cart.objects.get(student=self.user)
        self.society = Society.objects.get(name="KCL Tech society")
        self.event = Event.objects.get(pk=15)
        self.order = Order.objects.get(pk=29)
        self.url = reverse('order_detail', kwargs={'pk': self.order.id})
        self.other_user = Student.objects.get(email='evasmith@qmw.ac.uk')
        factory = RequestFactory()
        self.request = factory.get(self.url)
        self.request.user = self.user
        self.view = OrderDetailView()
        
    def test_url(self):
        self.assertEqual(self.url, f'/order_detail/{self.order.id}')
        
    def test_get_order_detail_page(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('order_detail', kwargs={'pk': self.order.id}))
        self.assertTemplateUsed(response, 'student/order_detail.html')
    
    def test_get_order_detail_returns_404_when_access_other_user_order(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        
    def test_get_order_detail_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_order_detail_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
        
    def test_get_object(self):
        self.client.login(email=self.user.email, password='Password123')
        self.view.setup(self.request, pk=self.order.pk)
        obj = self.view.get_object()
        self.assertIsInstance(obj, Order)
        self.assertEqual(obj.pk, self.order.pk)
        self.assertEqual(obj.student, self.user.student)
    
    def test_get_correct_data(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        # Test the response and template.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/order_detail.html')
        context = response.context
        # Test if the context data is correct.
        actual_total_price = response.context_data['total_price']
        expected_total_price = self.order.historicalcart.total_price
        actual_total_saved = response.context_data['total_saved']
        expected_total_saved = self.order.historicalcart.total_saved
        actual_event_cart_items = response.context_data['event_cart_items']
        expected_event_cart_items = self.order.historicalcart.event_cart_item.all()
        actual_memberships = response.context_data['memberships']
        expected_memberships = self.order.historicalcart.membership.all()
        actual_payment = response.context_data['payment']
        expected_payment = Payment.objects.get(order=self.order)
        self.assertEqual(actual_total_price, expected_total_price)
        self.assertEqual(actual_total_saved, expected_total_saved)
        self.assertEqual(list(actual_event_cart_items), list(expected_event_cart_items))
        self.assertEqual(list(actual_memberships), list(expected_memberships))
        self.assertEqual(actual_payment, expected_payment)
        