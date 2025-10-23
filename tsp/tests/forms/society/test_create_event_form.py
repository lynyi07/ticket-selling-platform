"""Unit tests of the create event form"""
import os
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from tsp.models import Society, Event
from tsp.forms.society.create_event_form import CreateEventForm
from django import forms

class CreateEventFormTestCase(TestCase):
    """Unit tests of the create event form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/other_universities.json',
        'tsp/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.default_photo = 'static/images/default_event_photo.jpg'
        self.form_input = {
            'name': 'Test Event',
            'description': 'This is a test event.',
            'location': 'Test location',
            'photo': self.default_photo,
            'start_time': timezone.now() + timezone.timedelta(days=1),
            'end_time': timezone.now() + timezone.timedelta(days=1, hours=2),
            'early_booking_capacity': 100,
            'standard_booking_capacity': 200,
            'early_bird_price': 3.0,
            'standard_price': 5.0,
            'partner_emails': 'robotics@qmw.ac.uk, ai_society@kcl.ac.uk'
        }
        self.society = Society.objects.get(email='robotics@qmw.ac.uk')

    def test_valid_form(self):
        form = CreateEventForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_blank_partner_emails(self):
        self.form_input['partner_emails'] = ''
        form = CreateEventForm(data = self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_partners(), [])

    def test_form_has_necessary_fields(self):
        form = CreateEventForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('end_time', form.fields)
        self.assertIn('early_booking_capacity', form.fields)
        self.assertIn('standard_booking_capacity', form.fields)
        self.assertIn('early_bird_price', form.fields)
        self.assertIn('standard_price', form.fields)
        self.assertIn('photo', form.fields)
        self.assertIn('partner_emails', form.fields)
        
    def test_duplicated_event_can_not_be_created(self):
        # Events with the same names, start_time and end_time are duplicated.
        # Since event has been created in set up, event with the same form input
        # can not be created.
        
        self._create_duplicate_event_object()
        form = CreateEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertEqual(
            form.errors['name'][0],
            "Event with the same name, start time and end time already exists."
        )
        self.assertIn('start_time', form.errors)
        self.assertEqual(
            form.errors['start_time'][0],
            "Event with the same name, start time and end time already exists."
        )
        self.assertIn('end_time', form.errors)
        self.assertEqual(
            form.errors['end_time'][0],
            "Event with the same name, start time and end time already exists."
        )

    def test_default_photo_if_no_photo_uploaded(self):
        event = CreateEventForm(data=self.form_input).save()
        self.assertEqual(event.photo.name, self.default_photo)

    def test_upload_photo(self):
        event = CreateEventForm(data=self.form_input).save()

        # Get the file path for the test photo
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_photo.jpg'
        )
        # Read the image data and assign it to the event photo
        with open(file_path, 'rb') as f:
            image_data = f.read()
            event.photo = SimpleUploadedFile(
                "test_photo.jpg",
                image_data,
                content_type="image/jpeg"
            )
        
        # Check if the photo has been updated
        self.assertEqual(event.photo.url, '/test_photo.jpg')

    def test_clean_partners_with_valid_partner_emails(self):
        form = CreateEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_partners(), [self.society, Society.objects.get(name='KCL AI society')])

    def test_clean_partners_with_invalid_partner_emails(self):
        self.form_input['partner_emails'] = 'robotics@qmw.ac.uk, ai_soc@kcl.ac.uk'
        form = CreateEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        try:
            form.clean_partners()
        except forms.ValidationError as error:
            self.assertIn("The following email addresses are invalid: ai_soc@kcl.ac.uk", form.errors['partner_emails'])
            self.assertEqual(forms.ValidationError(form.errors['partner_emails']).error_list, error.error_list)

    def test_form_save(self):
        before_count = Event.objects.count()
        CreateEventForm(data=self.form_input).save()
        after_count = Event.objects.count()
        self.assertEqual(before_count+1, after_count)

    def test_upload_photo_with_false_commit(self):
        event = CreateEventForm(data=self.form_input).save(commit=False)

        # Get the file path for the test photo
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_photo.jpg'
        )
        # Read the image data and assign it to the event photo
        with open(file_path, 'rb') as f:
            image_data = f.read()
            event.photo = SimpleUploadedFile(
                "test_photo.jpg",
                image_data,
                content_type="image/jpeg"
            )
        # Check if the photo has been updated
        self.assertEqual(event.photo.url, '/test_photo.jpg')

    def _create_duplicate_event_object(self):
        Event.objects.create(
            name= 'Test Event',
            description='This is a test event.',
            location='Test location',
            photo=self.default_photo,
            start_time=self.form_input['start_time'],
            end_time=self.form_input['end_time'],
            early_booking_capacity=100,
            standard_booking_capacity=200,
            early_bird_price=3.0,
            standard_price=5.0,
        )