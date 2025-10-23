"""Unit tests of the events tickets view"""
from django.test import TestCase
from django.utils import timezone
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event

class EventsTicketsViewTestCase(TestCase):
    """Unit tests of the events list view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.other_user = Society.objects.get(email='ai_society@kcl.ac.uk')
        self.event = Event.objects.get(pk=15)
        self.url = reverse('event_tickets', kwargs={'pk':self.event.id})


    def test_events_list_url(self):
        self.assertEqual(self.url, f'/event_tickets/{self.event.id}/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'society/event_tickets.html')

    def test_get_event_tickets_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_event_tickets_returns_404_when_access_event_not_organised_by_own_society(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_event_tickets_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_event_tickets_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

