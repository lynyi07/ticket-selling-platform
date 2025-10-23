"""Unit tests of the events list view"""
from django.test import TestCase
from django.utils import timezone
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event

class EventsListViewTestCase(TestCase):
    """Unit tests of the events list view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('events_list')
        self.event = Event.objects.get(pk=15)

    def test_events_list_url(self):
        self.assertEqual(self.url,'/events_list/')

    def test_view_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('events_list'))
        self.assertTemplateUsed(response, 'society/events_list.html')

    def test_get_events_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_events_list_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_events_list_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')
        
    def test_view_displays_upcoming_events_by_default(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['object_list'], [self.event])

    def test_view_displays_upcoming_events(self):
        self.event.start_time = timezone.now() + timezone.timedelta(days=1)
        self.event.end_time = timezone.now() + timezone.timedelta(days=1, hours=2)
        self.event.save()
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, {'event_type': 'UPCOMING'})
        self.assertQuerysetEqual(response.context['object_list'], [self.event])

    def test_view_displays_past_events(self):
        self.event.start_time = timezone.now() - timezone.timedelta(days=1)
        self.event.end_time = timezone.now() - timezone.timedelta(days=1, hours=2)
        self.event.save()
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, {'event_type': 'PAST'})
        self.assertQuerysetEqual(response.context['object_list'], [self.event])

    def test_view_displays_cancelled_events(self):
        self.event.status = self.event.Status.CANCELLED
        self.event.save()
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, {'event_type': 'CANCELLED'})
        self.assertQuerysetEqual(response.context['object_list'], [self.event])
        
    def test_search_event_by_name(self):
        self.client.login(email=self.user.email, password='Password123')
        name = self.event.name
        response = self.client.get(self.url, {'search': name})
        self.assertContains(response, name)
