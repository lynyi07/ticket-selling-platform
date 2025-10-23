"""Unit tests of the modify event view"""
import os
from ticket_selling_platform import settings
from django.test import TestCase
from django.utils import timezone
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from django.core import mail
from tsp.models import Society, Event, Student
from tsp.forms.society.modify_event_form import ModifyEventForm

class ModifyEventViewTestCase(TestCase):
    """Unit tests of the modify event view"""

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
        self.default_photo = os.path.join(
            settings.MEDIA_ROOT,
            'default_event_photo.jpg'
        )
        self.start_time = timezone.now() + timezone.timedelta(days=1)
        self.end_time = timezone.now() + timezone.timedelta(days=1, hours=2)
        self.form_input = {
            'name': 'New Test Event',
            'description': 'This is a new test event.',
            'location': 'New Test Location',
            'photo': self.default_photo,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'early_booking_capacity': 100,
            'standard_booking_capacity': 200,
            'early_bird_price': 3.0,
            'standard_price': 5.0,
        }
        self.event = Event.objects.get(pk=15)
        self.event.start_time = self.start_time
        self.event.end_time = self.end_time
        self.event.photo = self.default_photo
        self.event.save()
        self.event.society.add(self.user)
        self.url = reverse('modify_event', kwargs={'pk':self.event.pk})
    
    def test_request_url(self):
        self.assertEqual(self.url, '/modify_event/' + str(self.event.pk) + '/')
        
    def test_get_request(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/modify_event.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ModifyEventForm))

    def test_get_request_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def test_get_modify_event_returns_404_when_access_event_not_organised_by_own_society(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_member_event_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_member_event_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_successful_event_modify(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = Event.objects.count()
        # modify_event_url = reverse('modify_event', args=[self.event.id])
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'society/event_detail.html')
        response_url = reverse('event_detail', args=[self.event.id])
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

        # Test that the event fields are updated correctly
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, self.form_input['name'])
        self.assertEqual(self.event.start_time, self.form_input['start_time'])
        self.assertEqual(self.event.end_time, self.form_input['end_time'])
        self.assertEqual(self.event.description, self.form_input['description'])
        self.assertEqual(self.event.location, self.form_input['location'])
        self.assertEqual(self.event.standard_booking_capacity, self.form_input['standard_booking_capacity'])
        self.assertEqual(self.event.early_booking_capacity, self.form_input['early_booking_capacity'])
        self.assertEqual(self.event.early_bird_price, self.form_input['early_bird_price'])
        self.assertEqual(self.event.standard_price, self.form_input['standard_price'])
        self.assertEqual(self.event.photo, self.form_input['photo'])
    
    def test_send_event_notification(self):
        self.client.login(email=self.user.email, password='Password123')
        student = Student.objects.get(email='johndoe@kcl.ac.uk')
        student.saved_event.add(self.event)
        form = ModifyEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Changes to ' + self.event.name )
        self.assertEqual(mail.outbox[0].to, ['johndoe@kcl.ac.uk'])
        
    def test_event_modify_with_invalid_start_time_in_the_past(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = Event.objects.count()
        self.form_input['start_time'] = timezone.now()-timezone.timedelta(days=1)
        self.modify_event_url = reverse('modify_event', args=[self.event.id])
        response = self.client.post(self.modify_event_url, self.form_input, follow=True)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'society/modify_event.html')
        self._check_event_is_not_modified()
    
    def test_event_modify_with_end_time_earlier_than_start_time(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = Event.objects.count()
        self.form_input['end_time'] = self.start_time-timezone.timedelta(days=1)
        self.modify_event_url = reverse('modify_event', args=[self.event.id])
        response = self.client.post(self.modify_event_url, self.form_input, follow=True)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'society/modify_event.html')
        self._check_event_is_not_modified()
    
    def test_event_modify_with_decreasing_standard_booking_capacity(self):
        self.client.login(username=self.user.email, password='Password123')
        before_count = Event.objects.count()
        self.form_input['standard_booking_capacity'] = self.event.standard_booking_capacity-1
        self.modify_event_url = reverse('modify_event', args=[self.event.id])
        response = self.client.post(self.modify_event_url, self.form_input, follow=True)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'society/modify_event.html')
        self._check_event_is_not_modified()

    def _check_event_is_not_modified(self):
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, 'Default test event')
        self.assertEqual(self.event.description, 'This is a default test event')
        self.assertEqual(self.event.location, 'Default test location')
        self.assertEqual(self.event.start_time, self.start_time)
        self.assertEqual(self.event.end_time, self.end_time)
        self.assertEqual(self.event.early_booking_capacity, 50)
        self.assertEqual(self.event.standard_booking_capacity, 100)
        self.assertEqual(self.event.early_bird_price, 3.0)
        self.assertEqual(self.event.standard_price, 5.0)
        self.assertEqual(self.event.photo, self.default_photo)
