"""Unit tests of the save event view for a student account"""
from django.test import TestCase
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Event, Student

class SaveEventTestCase(TestCase):
    """Unit tests of the save event view for a student account"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.event = Event.objects.get(pk=15)
        self.url = reverse('save_event')
    
    def test_url(self):
        self.assertEqual(self.url, '/save_event/')
        
    def test_successful_save_event(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.post(self.url, {'event_pk': self.event.pk}, follow=True)
        redirected_url = reverse('event_page', kwargs={'pk': self.event.pk})
        self.assertRedirects(response, redirected_url, 302, 200)
        self.assertTrue(self.user.event_saved(self.event))
    
    def test_successful_unsave_event(self):
        self.user.save_event(self.event)
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.post(self.url, {'event_pk': self.event.pk}, follow=True)
        redirected_url = reverse('event_page', kwargs={'pk': self.event.pk})
        self.assertRedirects(response, redirected_url, 302, 200)
        self.assertFalse(self.user.event_saved(self.event)) 
    
    def test_get_save_event_redirects_when_logged_in_with_a_society_account(self):
        self.client.login(email='tech_society@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_save_event_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')