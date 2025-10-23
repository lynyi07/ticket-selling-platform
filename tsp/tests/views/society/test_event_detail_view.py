"""Unit tests of the event detail view"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event

class EventDetailViewTestCase(TestCase):
    """Unit tests of the event detail view"""

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
        self.event = Event.objects.get(name='Default test event')
        self.url = reverse('event_detail', kwargs={'pk': self.event.pk})
    
    def test_request_url(self):
        self.assertEqual(self.url, '/event_detail/' + str(self.event.pk) + '/')

    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/event_detail.html')

    def test_get_request_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_event_detail_returns_404_when_access_event_not_organised_by_own_society(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_event_detail_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_event_detail_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_event_detail_displays_correct_information(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('event_detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/event_detail.html')
        self.assertEqual(response.context['event'], self.event)
    
    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        events_list_url = reverse('events_list')
        self.assertContains(response, events_list_url)
        event_tickets_url = reverse('event_tickets', kwargs={'pk':self.event.id})
        self.assertContains(response, event_tickets_url)
        modify_event_url = reverse('modify_event', kwargs={'pk':self.event.id})
        self.assertContains(response, modify_event_url)

 