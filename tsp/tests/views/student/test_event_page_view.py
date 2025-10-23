"""Unit tests of the event page view"""
from django.test import TestCase
from django.urls import reverse
from tsp.models import Society, Event, Student
from django.utils import timezone
from datetime import timedelta

class EventPageViewTestCase(TestCase):
    """Unit tests of the event page view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.other_user = Student.objects.get(email='evasmith@qmw.ac.uk')
        self.society = Society.objects.get(name="KCL Tech society")
        self.event = Event.objects.get(pk=15)
        self.url = reverse('event_page', kwargs={'pk': self.event.id})

    def test_url(self):
        self.assertEqual(self.url, f'/event_page/{self.event.id}/')

    def test_get_event_page(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('event_page', kwargs={'pk': self.event.id}))
        self.assertTemplateUsed(response, 'student/event_page.html')
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['form'].event, self.event)
    
    def test_get_event_page_returns_404_when_access_event_in_other_university(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_event_page_with_cancelled_event(self):
        self.event.satus = 'CANCELLED'
        self.event.save()
        self.event.society.add(self.society)
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('event_page', kwargs={'pk': self.event.id}))
        self.assertTemplateUsed(response, 'student/event_page.html')
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(
            response.context['form'].event, 
            Event.objects.filter(status='ACTIVE').first()
        )

    def test_get_event_page_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_event_page_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_button_links_present(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        all_events_url = reverse('all_events')
        self.assertContains(response, all_events_url)
        save_society_event_url = reverse('save_event')
        self.assertContains(response, save_society_event_url)
