"""Unit tests of the ticket detail view"""
from django.test import TestCase
from django.urls import reverse
from django.test import RequestFactory
from tsp.models import User, Event, Student, Order, Ticket
from tsp.views.student.ticket_view import TicketView

class TicketViewTestCase(TestCase):
    """Unit tests of the ticket detail view"""

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
        self.event = Event.objects.get(pk=15)
        self.order = Order.objects.get(pk=29)
        self.other_user = Student.objects.get(email='evasmith@qmw.ac.uk')
        self.url = reverse('tickets', kwargs={'pk': self.order.pk})
        
    def test_url(self):
        self.assertEqual(self.url, f'/order_detail/{self.order.id}/tickets/')
    
    def test_get_tickets_page(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'student/tickets.html')
    
    def test_get_tickets_page_returns_404_when_access_other_user_tickets(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        
    def test_get_tickets_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_tickets_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_get_context_data(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        # Test the response and template.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/tickets.html')
        context = response.context
        # Test if the context data is correct.
        self.assertIn('tickets', context)
        tickets = context['tickets']
        actual_tickets = tickets
        expected_tickets = Ticket.objects.filter(order=self.order)
        self.assertEqual(list(actual_tickets), list(expected_tickets))
        self.assertTrue(ticket.event == self.event for ticket in tickets)