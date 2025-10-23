"""Unit tests of the cancel event view"""
from django.test import TestCase
from tsp.models import Society, Event, Student
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from django.core import mail
from datetime import timedelta
from django.utils import timezone

class CancelEventViewTestCase(TestCase):
    """Unit tests of the cancel event view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.event = Event.objects.get(pk=15)
        self.student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.student.saved_event.add(self.event)
        self.student.purchased_event.add(self.event)
        self.url = reverse('cancel_event')

    def test_cancel_event_url(self):
        self.assertEqual(self.url, '/cancel_event')

    def test_successful_event_cancel(self):
        self.client.login(email=self.user.email, password='Password123')
        event_count_before = Event.objects.count()
        cancel_event_url = reverse('cancel_event')
        response = self.client.post(cancel_event_url, {'event_id': self.event.id}, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, 'CANCELLED')       
        response_url = reverse('events_list')
        self.assertTemplateUsed(response, 'society/events_list.html')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"We're sorry, the event {self.event.name} is cancelled!")
        self.assertEqual(mail.outbox[0].to, ['johndoe@kcl.ac.uk'])
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_get_cancel_event_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_cancel_event_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_cancel_event_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')