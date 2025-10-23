"""Unit tests of the base event form"""
import os
from ticket_selling_platform import settings
from django.test import TestCase
from django.utils import timezone
from tsp.models import Society, Event
from tsp.forms.society.base_event_form import BaseEventForm

class BaseEventFormTestCase(TestCase):
    """Unit tests of the base event form"""

    fixtures = [
        'tsp/tests/fixtures/default_user.json',
        'tsp/tests/fixtures/default_university.json',
        'tsp/tests/fixtures/default_event.json'
    ]

    def setUp(self):
        self.user = Society.objects.get(email='tech_society@kcl.ac.uk')
        self.default_photo = os.path.join(
            settings.MEDIA_ROOT,
            'default_event_photo.jpg'
        )
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
        }

    def test_valid_form(self):
        form = BaseEventForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def test_form_has_necessary_fields(self):
        form = BaseEventForm()
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
        
    def test_start_time_must_not_be_in_the_past(self):
        data = self.form_input
        data['start_time'] = timezone.now() - timezone.timedelta(days=1)
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('start_time', form.errors)
        self.assertEqual(
            form.errors['start_time'][0], 
            "Start time can't be in the past."
        )

    def test_end_time_must_be_after_start_time(self):
        start_time = self.form_input['start_time']
        data = self.form_input
        data['end_time'] = start_time - timezone.timedelta(hours=1)
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('end_time', form.errors)
        self.assertEqual(
            form.errors['end_time'][0], 
            "End time must be after start time."
        )

    def test_early_booking_capacity_must_not_be_negative(self):
        data = self.form_input
        data['early_booking_capacity'] = -1
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('early_booking_capacity', form.errors)
        self.assertEqual(
            form.errors['early_booking_capacity'][0], 
            "This value can't be negative."
        )
        
    def test_standard_booking_capacity_must_not_be_negative(self):
        data = self.form_input
        data['standard_booking_capacity'] = -1
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('standard_booking_capacity', form.errors)
        self.assertEqual(
            form.errors['standard_booking_capacity'][0], 
            "This value can't be negative."
        )
        
    def test_standard_price_must_be_higher_than_early_bird_price(self):
        data = self.form_input
        data['early_bird_price'] = 10.0
        data['standard_price'] = 6.5
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('standard_price', form.errors)
        self.assertEqual(
            form.errors['standard_price'][0], 
            "Standard price must be higher than early bird price."
        )
        
    def test_early_bird_price_must_not_be_negative(self):
        data = self.form_input
        data['early_bird_price'] = -1.5
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('early_bird_price', form.errors)
        self.assertEqual(
            form.errors['early_bird_price'][0], 
            "This value can't be negative."
        )

    def test_prices_must_not_be_negative(self):
        data = self.form_input
        data['early_bird_price'] = -1.5
        data['standard_price'] = -2.5
        form = BaseEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('standard_price', form.errors)
        self.assertIn('early_bird_price', form.errors)
        self.assertEqual(
            form.errors['early_bird_price'][0], 
            "This value can't be negative."
        )
        self.assertEqual(
            form.errors['standard_price'][0], 
            "This value can't be negative."
        )
    
    def test_clean_duplicate_events(self):
        event = Event.objects.get(pk=15)
        self.form_input['name'] = event.name
        self.form_input['start_time'] = event.start_time
        self.form_input['end_time'] = event.end_time
        existing_events = self._get_existing_events()
        form = BaseEventForm(data=self.form_input)
        form.clean_duplicate_events(existing_events)
        self.assertIn("Event with the same name, start time and end time already exists.", form.errors['name'])
        self.assertIn("Event with the same name, start time and end time already exists.", form.errors['start_time'])
        self.assertIn("Event with the same name, start time and end time already exists.", form.errors['end_time'])

    def test_clean_duplicate_events_returns_None(self):
        existing_events = self._get_existing_events()
        form = BaseEventForm(data=self.form_input)
        self.assertEqual(form.clean_duplicate_events(existing_events), None)

    def _get_existing_events(self):
        return Event.objects.filter(
            name=self.form_input['name'],
            start_time=self.form_input['start_time'],
            end_time=self.form_input['end_time']
        )