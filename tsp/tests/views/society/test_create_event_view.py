"""Unit tests of the create event view"""
import os
from ticket_selling_platform import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from tsp.tests.helpers import reverse_with_next
from django.urls import reverse
from tsp.models import Society, Event, Student
from tsp.forms.society.create_event_form import CreateEventForm
from django.core import mail

class CreateEventViewTestCase(TestCase):
    """Unit tests of the create event view"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/other_users.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.url = reverse('create_event')
        self.default_photo = os.path.join(
            settings.MEDIA_ROOT,
            'default_event_photo.jpg'
        )
        self.form_input = {
            'name': 'Test Event',
            'description': 'This is a test event.',
            'location': 'Test location',
            'start_time': timezone.now() + timezone.timedelta(days=1),
            'end_time': timezone.now() + timezone.timedelta(days=1, hours=2),
            'early_booking_capacity': 100,
            'standard_booking_capacity': 200,
            'early_bird_price': 3.0,
            'standard_price': 5.0,
        }
        self.event = Event.objects.create(**self.form_input)
        self.form_input['partner_emails'] = 'robotics@qmw.ac.uk, ai_society@kcl.ac.uk'
        self.event.society.add(self.user)
        self.event.save()

    def test_url(self):
        self.assertEqual(self.url, '/create_event/')

    def test_get_create_event(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'society/create_event.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateEventForm))

    def test_get_create_event_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_event_redirects_when_logged_in_with_a_student_account(self):
        self.client.login(email='johndoe@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_get_create_event_redirects_when_logged_in_with_a_student_union_account(self):
        self.client.login(email='kclsu@kcl.ac.uk', password='Password123')
        redirect_url = reverse('landing')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_succesful_event_create(self):
        self.client.login(email=self.user.email, password='Password123')
        event_count_before = Event.objects.count()
        # Update event name as event with the form input data has been created.
        # Duplicated event (the same name, start_time and end_time is not
        # allowed to be created.
        self.form_input['name'] = 'Test Event Name'
        form = CreateEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.url, self.form_input, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before+1)
        event = Event.objects.get(name='Test Event Name')
        self.assertEqual(list(event.society.all()), list(Society.objects.all()))
        response_url = reverse('create_event')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'society/create_event.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_default_photo_if_no_photo_uploaded(self):
        self.assertEqual(self.event.photo.path, self.default_photo)

    def test_photo_upload(self):
        # Get the file path for the test photo
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_photo.jpg'
        )
        # Read the image data and assign it to the event photo
        with open(file_path, 'rb') as f:
            image_data = f.read()
            photo = SimpleUploadedFile(
                "test_photo.jpg",
                image_data,
                content_type="image/jpeg"
            )
        data = {
            **self.form_input,
            'photo': photo
        }
        # Update event name as event with the form input data has been created.
        # Duplicated event (the same name, start_time and end_time is not
        # allowed to be created.
        data['name'] = 'Test Event Name'
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertTrue(self.event.photo)
        # Check if the uploaded photo has the same content as the original photo
        uploaded_photo = self.event.photo.open()
        uploaded_image_data = uploaded_photo.read()
        self.assertEqual(image_data, uploaded_image_data)

    def test_duplicated_event_can_not_be_created(self):
        # Events with the same names, start_time and end_time are duplicated.
        # Since event has been created in set up, event with the same form input
        # can not be created.
        self.client.login(email=self.user.email, password='Password123')
        event_count_before = Event.objects.count()
        data=self.form_input
        form = CreateEventForm(data)
        self.assertFalse(form.is_valid())
        response = self.client.post(self.url, data, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        self.assertTemplateUsed(response, 'society/create_event.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_form_with_invalid_partners(self):
        self.client.login(email=self.user.email, password='Password123')
        event_count_before = Event.objects.count()
        self.form_input['partner_emails'] = 'robotics@qmw.ac.uk, ai@kcl.ac.uk'
        form = CreateEventForm(self.form_input)
        self.assertFalse(form.is_valid())
        response = self.client.post(self.url, self.form_input, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_event_cannot_be_created_without_bank_details(self):
        self.client.login(email='robotics@qmw.ac.uk', password='Password123')
        event_count_before = Event.objects.count()
        # Update event name as event with the form input data has been created.
        # Duplicated event (the same name, start_time and end_time is not
        # allowed to be created.
        self.form_input['name'] = 'Test Event Name'
        form = CreateEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.url, self.form_input, follow=True)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 2)

    def test_send_event_notification(self):
        self.client.login(email=self.user.email, password='Password123')
        student = Student.objects.get(email='johndoe@kcl.ac.uk')
        self.user.subscriber.add(student)
        self.form_input['name'] = 'Test Event Name'
        form = CreateEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "KCL Tech society has created a new event!")
        self.assertEqual(mail.outbox[0].to, ["johndoe@kcl.ac.uk"])